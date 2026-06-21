import json

import geeskill.cli as cli
from geeskill.errors import error_payload
from geeskill.hk_ndvi_preflight import HKNDVIPreflightConfig, run_hk_ndvi_preflight


class FakeProbe:
    def __init__(
        self,
        *,
        district_count=18,
        selected_count=1,
        image_count=5,
        filtered_count=3,
        ndvi=True,
        dynamic_world_count=4,
        landcover_label=True,
        landcover_probabilities=True,
        class_fractions=None,
    ):
        self.district_count = district_count
        self.selected_count = selected_count
        self.image_count = image_count
        self.filtered_count = filtered_count
        self.ndvi = ndvi
        self.dynamic_world_count = dynamic_world_count
        self.landcover_label = landcover_label
        self.landcover_probabilities = landcover_probabilities
        self.class_fractions = class_fractions or {
            "water": 0.42,
            "built": 0.25,
            "vegetation": 0.18,
            "trees": 0.12,
            "grass": 0.04,
        }

    def initialize(self):
        self.initialized = True

    def probe_district_source(self):
        return {
            "district_source": "fake.geojson",
            "district_source_type": "local_geojson",
            "district_property": "District",
            "district_feature_count": self.district_count,
            "admin_property_names": ["District"],
            "sample_district_names": ["Central & Western", "Eastern"],
        }

    def select_district(self, district_name, district_names):
        return {
            "requested_district": district_name,
            "selected_district_name": None if district_name is None else "Central & Western" if self.selected_count else district_name,
            "selected_district_count": self.selected_count,
            "selected_geometry_area_m2": 1000 if self.selected_count else None,
        }

    def probe_images(self, year, month):
        bands = ["B4", "B8", "SCL", "NDVI"] if self.ndvi else ["B4", "B8", "SCL"]
        ndvi_bands = ["NDVI"] if self.ndvi else []
        return {
            "date_start": f"{year}-{month:02d}-01",
            "date_end": f"{year}-{month + 1:02d}-01",
            "s2_image_count": self.image_count,
            "s2_cloud_filtered_image_count": self.filtered_count,
            "first_image_band_names_after_ndvi": bands,
            "monthly_ndvi_band_names": ndvi_bands,
            "sanity_stat": {"NDVI": 0.4} if self.ndvi else {},
        }

    def probe_landcover(self, year, month):
        bands = ["label"] if self.landcover_label else []
        if self.landcover_probabilities:
            bands.extend(["water", "trees", "grass", "flooded_vegetation", "crops", "shrub_and_scrub", "built", "bare", "snow_and_ice"])
        return {
            "landcover_dataset_id": "GOOGLE/DYNAMICWORLD/V1",
            "landcover_strategy": "dynamic_world_time_matched_probability_masks",
            "dynamic_world_probability_threshold": 0.35,
            "dynamic_world_image_count": self.dynamic_world_count,
            "dynamic_world_band_names": bands,
            "missing_probability_bands": [] if self.landcover_probabilities else ["water"],
            "has_label_band": self.landcover_label,
            "class_fractions": self.class_fractions,
            "ndvi_probes": {
                "all_surface_mean_ndvi": 0.08,
                "non_water_mean_ndvi": 0.16,
                "vegetation_mean_ndvi": 0.45,
                "built_mean_ndvi": 0.06,
                "water_mean_ndvi": -0.02,
            },
            "warnings": [],
        }


def _config():
    return HKNDVIPreflightConfig(
        project="example-project",
        year=2024,
        month=1,
        district="Central and Western",
    )


def _landcover_config():
    return HKNDVIPreflightConfig(
        project="example-project",
        year=2024,
        month=1,
        scope="hong-kong",
        landcover="dynamic-world",
        landcover_dataset_id="GOOGLE/DYNAMICWORLD/V1",
        landcover_strategy="dynamic_world_time_matched_probability_masks",
        dynamic_world_probability_threshold=0.35,
    )


def test_preflight_succeeds_when_districts_and_images_are_non_empty():
    report = run_hk_ndvi_preflight(_config(), probe=FakeProbe())
    assert report["ok"] is True
    assert report["decision"] == "allow_export"
    assert report["checks"]["selected_district"]["selected_district_name"] == "Central & Western"


def test_preflight_succeeds_for_whole_hong_kong_scope():
    config = HKNDVIPreflightConfig(project="example-project", year=2024, month=1, scope="hong-kong")
    report = run_hk_ndvi_preflight(config, probe=FakeProbe(selected_count=18))
    assert report["ok"] is True
    assert report["aoi_name"] == "Hong Kong"
    assert report["image_count_before_cloud_filter"] == 5
    assert report["image_count_after_cloud_filter"] == 3
    assert report["band_names"] == ["NDVI"]
    assert report["mean_ndvi_probe"] == 0.4


def test_preflight_fails_with_empty_aoi():
    report = run_hk_ndvi_preflight(_config(), probe=FakeProbe(district_count=0))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "EMPTY_AOI"


def test_preflight_fails_with_district_not_found():
    report = run_hk_ndvi_preflight(_config(), probe=FakeProbe(selected_count=0))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "DISTRICT_NOT_FOUND"
    assert "Central & Western" in report["critical_error"]["message"]


def test_preflight_fails_with_empty_image_collection():
    report = run_hk_ndvi_preflight(_config(), probe=FakeProbe(image_count=0))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "EMPTY_IMAGE_COLLECTION"


def test_preflight_fails_with_empty_filtered_collection():
    report = run_hk_ndvi_preflight(_config(), probe=FakeProbe(image_count=5, filtered_count=0))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "EMPTY_FILTERED_COLLECTION"


def test_preflight_fails_with_no_ndvi_band():
    report = run_hk_ndvi_preflight(_config(), probe=FakeProbe(ndvi=False))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "NO_NDVI_BAND"


def test_landcover_preflight_succeeds_with_non_empty_dynamic_world():
    report = run_hk_ndvi_preflight(_landcover_config(), probe=FakeProbe())
    assert report["ok"] is True
    assert report["dynamic_world_image_count"] == 4
    assert report["landcover_diagnostics"]["class_fractions"]["vegetation"] == 0.18


def test_landcover_preflight_fails_with_empty_s2_collection():
    report = run_hk_ndvi_preflight(_landcover_config(), probe=FakeProbe(image_count=0))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "EMPTY_S2_COLLECTION"


def test_landcover_preflight_fails_with_empty_dynamic_world_collection():
    report = run_hk_ndvi_preflight(_landcover_config(), probe=FakeProbe(dynamic_world_count=0))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "EMPTY_DYNAMIC_WORLD_COLLECTION"


def test_landcover_preflight_fails_with_missing_label_band():
    report = run_hk_ndvi_preflight(_landcover_config(), probe=FakeProbe(landcover_label=False))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "NO_LANDCOVER_LABEL"


def test_landcover_preflight_fails_with_missing_probability_bands():
    report = run_hk_ndvi_preflight(_landcover_config(), probe=FakeProbe(landcover_probabilities=False))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "NO_PROBABILITY_BANDS"


def test_landcover_preflight_fails_when_core_class_fractions_are_null():
    fractions = {"water": None, "built": None, "vegetation": None, "trees": None, "grass": None}
    report = run_hk_ndvi_preflight(_landcover_config(), probe=FakeProbe(class_fractions=fractions))
    assert report["ok"] is False
    assert report["critical_error"]["category"] == "CLASS_MASK_EMPTY"


def test_live_smoke_refuses_export_when_preflight_fails(monkeypatch, capsys):
    def fake_preflight(config):
        return {
            "ok": False,
            "decision": "block_export",
            "critical_error": error_payload("EMPTY_AOI", "No district features."),
            "checks": {},
        }

    def fail_execute(*args, **kwargs):
        raise AssertionError("execute_script should not be called after failed preflight")

    monkeypatch.setattr(cli, "run_hk_ndvi_preflight", fake_preflight)
    monkeypatch.setattr(cli, "execute_script", fail_execute)
    rc = cli.main(
        [
            "live-smoke-test",
            "--project",
            "example-project",
            "--confirm-live",
            "--smoke-month",
            "1",
            "--smoke-region",
            "Central and Western",
            "--export-folder",
            "gee_exports",
            "--run-id",
            "test-live-smoke-preflight-block",
        ]
    )
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error"]["category"] == "EMPTY_AOI"
