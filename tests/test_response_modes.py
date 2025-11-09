"""
Tests for response_modes service
"""
import pytest
from app.services.response_modes import RESPONSE_MODES, get_mode_config


class TestResponseModes:
    """Test cases for response modes configuration"""

    def test_response_modes_exists(self):
        """Test that RESPONSE_MODES dictionary exists"""
        assert RESPONSE_MODES is not None
        assert isinstance(RESPONSE_MODES, dict)

    def test_all_five_modes_exist(self):
        """Test that all 5 modes are defined"""
        expected_modes = ['tender', 'quick', 'analysis', 'strategy', 'checklist']
        assert len(RESPONSE_MODES) == 5
        for mode in expected_modes:
            assert mode in RESPONSE_MODES

    def test_tender_mode_configuration(self):
        """Test tender mode has correct configuration"""
        mode = RESPONSE_MODES['tender']
        assert mode['name'] == 'Tender Response'
        assert mode['icon'] == '📋'
        assert mode['description'] == 'Formal, polished responses for tender submissions'
        assert mode['temperature'] == 0.3
        assert 'system_prompt' in mode
        assert 'tender response specialist' in mode['system_prompt'].lower()

    def test_quick_mode_configuration(self):
        """Test quick answer mode has correct configuration"""
        mode = RESPONSE_MODES['quick']
        assert mode['name'] == 'Quick Answer'
        assert mode['icon'] == '⚡'
        assert mode['description'] == 'Brief, bullet-point answers'
        assert mode['temperature'] == 0.5
        assert 'system_prompt' in mode
        assert 'concise' in mode['system_prompt'].lower()

    def test_analysis_mode_configuration(self):
        """Test deep analysis mode has correct configuration"""
        mode = RESPONSE_MODES['analysis']
        assert mode['name'] == 'Deep Analysis'
        assert mode['icon'] == '🔍'
        assert mode['description'] == 'Detailed insights with citations'
        assert mode['temperature'] == 0.4
        assert 'system_prompt' in mode
        assert 'comprehensive analysis' in mode['system_prompt'].lower()

    def test_strategy_mode_configuration(self):
        """Test strategy advisor mode has correct configuration"""
        mode = RESPONSE_MODES['strategy']
        assert mode['name'] == 'Strategy Advisor'
        assert mode['icon'] == '💡'
        assert mode['description'] == 'Recommendations and next steps'
        assert mode['temperature'] == 0.6
        assert 'system_prompt' in mode
        assert 'strategic' in mode['system_prompt'].lower()

    def test_checklist_mode_configuration(self):
        """Test compliance checklist mode has correct configuration"""
        mode = RESPONSE_MODES['checklist']
        assert mode['name'] == 'Compliance Checklist'
        assert mode['icon'] == '✅'
        assert mode['description'] == 'Action items and requirements'
        assert mode['temperature'] == 0.2
        assert 'system_prompt' in mode
        assert 'checklist' in mode['system_prompt'].lower()

    def test_get_mode_config_valid_mode(self):
        """Test getting configuration for a valid mode"""
        config = get_mode_config('tender')
        assert config is not None
        assert config['name'] == 'Tender Response'

    def test_get_mode_config_invalid_mode(self):
        """Test getting configuration for invalid mode returns default"""
        config = get_mode_config('invalid_mode')
        assert config is not None
        # Should return quick mode as default
        assert config['name'] == 'Quick Answer'

    def test_get_mode_config_none(self):
        """Test getting configuration with None returns default"""
        config = get_mode_config(None)
        assert config is not None
        assert config['name'] == 'Quick Answer'

    def test_all_modes_have_required_fields(self):
        """Test that all modes have required fields"""
        required_fields = ['name', 'system_prompt', 'temperature', 'icon', 'description']
        for mode_key, mode_config in RESPONSE_MODES.items():
            for field in required_fields:
                assert field in mode_config, f"Mode '{mode_key}' missing field '{field}'"

    def test_temperature_values_in_valid_range(self):
        """Test that all temperature values are between 0 and 1"""
        for mode_key, mode_config in RESPONSE_MODES.items():
            temp = mode_config['temperature']
            assert 0 <= temp <= 1, f"Mode '{mode_key}' has invalid temperature: {temp}"

    def test_system_prompts_are_non_empty(self):
        """Test that all system prompts are non-empty strings"""
        for mode_key, mode_config in RESPONSE_MODES.items():
            prompt = mode_config['system_prompt']
            assert isinstance(prompt, str), f"Mode '{mode_key}' prompt is not a string"
            assert len(prompt) > 50, f"Mode '{mode_key}' prompt is too short"
