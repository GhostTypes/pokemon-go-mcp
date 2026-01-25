"""Tests for Pokemon type lookup service."""

import pytest

from pogo_mcp.pokemon_types import (
    calculate_weaknesses_from_types,
    clear_type_cache,
    fetch_pokemon_types,
)


class TestPokemonTypes:
    """Test Pokemon type lookup functionality."""

    def test_calculate_weaknesses_from_types_single_type(self):
        """Test weakness calculation for single-type Pokemon."""
        # Fire type Pokemon
        weaknesses = calculate_weaknesses_from_types(["fire"])

        assert "double" in weaknesses
        assert "single" in weaknesses

        # Fire is weak to water, ground, rock
        single_weak = weaknesses["single"]
        assert "water" in single_weak
        assert "ground" in single_weak
        assert "rock" in single_weak

    def test_calculate_weaknesses_from_types_dual_type(self):
        """Test weakness calculation for dual-type Pokemon."""
        # Charizard: Fire/Flying
        weaknesses = calculate_weaknesses_from_types(["fire", "flying"])

        # Both weak to rock (double weakness)
        double_weak = weaknesses["double"]
        assert "rock" in double_weak

        # Fire weak to water, ground; Flying weak to electric, ice
        single_weak = weaknesses["single"]
        assert "water" in single_weak
        assert "electric" in single_weak

    def test_calculate_weaknesses_from_types_four_times_weak(self):
        """Test Pokemon with 4x weakness."""
        # Rock/Flying (like Aerodactyl) - 4x weak to electric? No, let's check
        # Actually: Flying is immune to ground, not weak to electric

        # Ice/Flying - 4x weak to rock (Ice weak to rock, Flying weak to rock)
        weaknesses = calculate_weaknesses_from_types(["ice", "flying"])

        double_weak = weaknesses["double"]
        assert "rock" in double_weak  # Both weak to rock

    def test_calculate_weaknesses_from_types_immunity(self):
        """Test Pokemon with immunities."""
        # Ghost type - immune to normal and fighting
        weaknesses = calculate_weaknesses_from_types(["ghost"])

        # Should not list normal/fighting as weaknesses due to immunity
        single_weak = weaknesses["single"]
        double_weak = weaknesses["double"]

        assert "normal" not in single_weak
        assert "fighting" not in single_weak
        assert "normal" not in double_weak
        assert "fighting" not in double_weak

    @pytest.mark.asyncio
    async def test_fetch_pokemon_types_mewtwo(self):
        """Test fetching types for Mewtwo from PokeAPI."""
        clear_type_cache()  # Clear cache to ensure fresh fetch

        data = await fetch_pokemon_types("Mewtwo")

        assert data is not None
        assert "name" in data
        assert data["name"] == "mewtwo" or data["name"] == "Mewtwo"
        assert "types" in data
        assert len(data["types"]) > 0
        # Mewtwo is Psychic type
        assert "psychic" in [t.lower() for t in data["types"]]
        assert "weaknesses" in data

    @pytest.mark.asyncio
    async def test_fetch_pokemon_types_charizard(self):
        """Test fetching types for Charizard from PokeAPI."""
        clear_type_cache()  # Clear cache to ensure fresh fetch

        data = await fetch_pokemon_types("Charizard")

        assert data is not None
        assert "types" in data
        assert len(data["types"]) == 2  # Fire/Flying
        types_lower = [t.lower() for t in data["types"]]
        assert "fire" in types_lower
        assert "flying" in types_lower

    @pytest.mark.asyncio
    async def test_fetch_pokemon_types_pikachu(self):
        """Test fetching types for Pikachu from PokeAPI."""
        clear_type_cache()  # Clear cache to ensure fresh fetch

        data = await fetch_pokemon_types("Pikachu")

        assert data is not None
        assert "types" in data
        assert len(data["types"]) == 1  # Electric
        assert "electric" in [t.lower() for t in data["types"]]

    @pytest.mark.asyncio
    async def test_fetch_pokemon_types_invalid(self):
        """Test fetching types for invalid Pokemon."""
        clear_type_cache()  # Clear cache

        data = await fetch_pokemon_types("NotARealPokemon999")

        assert data is None

    @pytest.mark.asyncio
    async def test_fetch_pokemon_types_caching(self):
        """Test that Pokemon type data is cached."""
        clear_type_cache()

        # First call
        data1 = await fetch_pokemon_types("Mewtwo")
        assert data1 is not None

        # Second call should use cache
        data2 = await fetch_pokemon_types("Mewtwo")
        assert data2 is not None
        assert data1["name"] == data2["name"]
        assert data1["types"] == data2["types"]

    @pytest.mark.asyncio
    async def test_fetch_pokemon_types_case_insensitive(self):
        """Test that Pokemon lookup is case-insensitive."""
        clear_type_cache()

        data1 = await fetch_pokemon_types("mewtwo")
        data2 = await fetch_pokemon_types("MEWTWO")
        data3 = await fetch_pokemon_types("Mewtwo")

        assert data1 is not None
        assert data2 is not None
        assert data3 is not None

        # All should return the same data
        assert data1["name"] == data2["name"] == data3["name"]

    @pytest.mark.asyncio
    async def test_fetch_pokemon_types_with_spaces(self):
        """Test Pokemon names with spaces get converted to hyphens."""
        clear_type_cache()

        # "Mr. Mime" in PokeAPI is "mr-mime"
        data = await fetch_pokemon_types("Mr Mime")

        # Should successfully fetch (either finds it or gracefully fails)
        # The implementation converts spaces to hyphens
        assert data is not None or "mr" in str(data).lower()

    def test_clear_type_cache(self):
        """Test clearing the type cache."""
        # This just ensures the function doesn't error
        clear_type_cache()
        assert True  # If we got here, it worked
