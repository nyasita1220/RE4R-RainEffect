# RE4R Rain Texture Swap

Auto texture swapping on wet state for Resident Evil 4 Remake.

Detects wet state (rain/water/puddles) and automatically swaps specified textures to their wet versions, reverting when dry.

## Features

- Auto-switches to wet textures when raining
- Triggers on any wet state (rain, water, puddles)
- Auto-reverts to original textures when dry
- Supports any texture slot (normal, albedo, roughness, etc.)

## Requirements

- [REFramework](https://github.com/praydog/REFramework) (RE4R version)
- Rain_ textures must be loaded by the game (via MDF reference)

## Quick Start

### 1. Make the Game Load Rain_ Textures

Rain_ textures must be referenced in an MDF file to be loaded by the game.
How to do this:

1. Create a dummy mesh object (any name, recommend empty model to not affect visuals)
2. Create an MDF file for the dummy object, referencing your Rain_ texture paths
3. The game will now load your replacement textures

### 2. Generate the Script

Run the config generator `RainEffect_Sawp_Generator.py` and follow the prompts:

```bash
python RainEffect_Sawp_Generator.py
```

### 3. Bundle with your Mod

Place the generated `.lua` file into `<ModFolder>/reframework/autorun/`

## File Structure Example

```
RESIDENT EVIL 4  BIOHAZARD RE4/
  reframework/
    autorun/
      MyMod_rain_texture_swap.lua   ← generated script
  natives/STM/_Chainsaw/
    Character/ch/cha0/cha000/00/
      cha000_00_NRMR.tex            ← original texture
      Rain_cha000_00_NRMR.tex       ← wet texture
```

## How It Works

1. Reads `chainsaw.WeatherManager._CurrentGlobalWetRate` to detect wet state
2. Scans all `via.render.Mesh` components in the scene
3. Matches configured texture paths
4. Swaps textures via `via.render.Mesh.setMaterialTexture`

## Technical Details

- Preload: scans scene once on load, caches target mesh references
- State changes only iterate cached targets (no full scene re-scan)
- Texture swaps execute in `BeginRendering` phase to avoid conflicts
- Uses `ResourceHolder` wrapper for engine compatibility

## Credits

- [REFramework](https://github.com/praydog/REFramework) by praydog
- [EMV-Engine](https://github.com/alphazolam/EMV-Engine) by alphaZomega
- [Weather FX](https://www.nexusmods.com/residentevil42023/mods/107) by SilverEzredes
