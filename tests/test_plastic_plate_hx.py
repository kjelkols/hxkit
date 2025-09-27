"""
Tests for the PlasticPlateHeatExchanger.
"""

import pytest
from hxkit import (
    PlasticPlateHeatExchanger,
    MoistAir,
    AirStream,
    Direction,
    PlasticPlateResults
)

@pytest.fixture
def basic_hx():
    """Provides a basic PlasticPlateHeatExchanger instance."""
    return PlasticPlateHeatExchanger(
        width=0.5,
        length=1.0,
        plate_thickness=0.001,
        channel_height=0.005,
        num_plates=50,
        grid_resolution=(5, 5)
    )

@pytest.fixture
def crossflow_streams():
    """Provides hot and cold air streams in a crossflow configuration."""
    hot_air = MoistAir(temperature=25.0, relative_humidity=60.0)
    cold_air = MoistAir(temperature=-10.0, relative_humidity=80.0)

    hot_stream = AirStream(hot_air, mass_flow=1.0, direction=Direction.NORTH)
    cold_stream = AirStream(cold_air, mass_flow=0.8, direction=Direction.EAST)
    return hot_stream, cold_stream

def test_instantiation(basic_hx):
    """Tests if the heat exchanger can be instantiated correctly."""
    assert basic_hx is not None
    assert basic_hx.geometry.width == 0.5
    assert basic_hx.grid is None  # Grid opprettes først ved analyze()
    assert basic_hx.grid_resolution == (5, 5)
    assert basic_hx.material.thermal_conductivity == 0.3

def test_analyze_returns_valid_results(basic_hx, crossflow_streams):
    """
    Tests that the analyze method returns a PlasticPlateResults object
    with sensible values.
    """
    hot_stream, cold_stream = crossflow_streams
    results = basic_hx.analyze(hot_stream, cold_stream)

    assert results is not None
    assert isinstance(results, PlasticPlateResults)
    
    # Check for sensible (non-zero, within reason) results
    assert results.effectiveness > 0.1 and results.effectiveness < 0.95
    assert results.heat_transfer_rate > 0
    
    # Check that outlet states are different from inlet states
    assert results.hot_outlet_state.temperature < hot_stream.moist_air.temperature
    assert results.cold_outlet_state.temperature > cold_stream.moist_air.temperature
    
    # Check that fields are populated  
    assert results.plate_temperature_field is not None
    assert results.plate_temperature_field.shape == (5, 5)
    
    # Verify that grid was created correctly for crossflow
    assert basic_hx.grid is not None
    assert basic_hx.grid.width_segments == 5
    assert basic_hx.grid.length_segments == 5

def test_counterflow_optimization(basic_hx):
    """Tests that 1D optimization works for counterflow configurations."""
    hot_air = MoistAir(temperature=25.0, relative_humidity=60.0)
    cold_air = MoistAir(temperature=10.0, relative_humidity=50.0)

    # Counterflow: North vs South
    hot_stream = AirStream(hot_air, mass_flow=1.0, direction=Direction.NORTH)
    cold_stream = AirStream(cold_air, mass_flow=1.0, direction=Direction.SOUTH)
    
    results = basic_hx.analyze(hot_stream, cold_stream)
    
    # Should create 1D grid along width (Y-direction)
    assert basic_hx.grid.width_segments == 5  # max(5,5) = 5
    assert basic_hx.grid.length_segments == 1  # Optimized to 1
    
    # Results should still be valid
    assert results.effectiveness > 0.0
    assert results.heat_transfer_rate > 0.0

def test_parallelflow_optimization(basic_hx):
    """Tests that 1D optimization works for parallel flow configurations."""
    hot_air = MoistAir(temperature=25.0, relative_humidity=60.0)
    cold_air = MoistAir(temperature=10.0, relative_humidity=50.0)

    # Parallel flow: both going East
    hot_stream = AirStream(hot_air, mass_flow=1.0, direction=Direction.EAST)
    cold_stream = AirStream(cold_air, mass_flow=1.0, direction=Direction.EAST)
    
    results = basic_hx.analyze(hot_stream, cold_stream)
    
    # Should create 1D grid along length (X-direction) 
    assert basic_hx.grid.width_segments == 1    # Optimized to 1
    assert basic_hx.grid.length_segments == 5   # max(5,5) = 5
    
    # Results should still be valid
    assert results.effectiveness > 0.0
    assert results.heat_transfer_rate > 0.0
