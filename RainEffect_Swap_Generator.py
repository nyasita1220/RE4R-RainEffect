#!/usr/bin/env python3
"""RE4R 湿身换贴图 - 配置生成器 | 生成器作者: NyaSita"""

import os
from datetime import datetime

TEMPLATE = r"""--============================================================
-- RE4R 湿身换贴图
-- 生成器作者: NyaSita
-- 生成时间: {time}
--============================================================

local SWAP_LIST = {{
{paths}
}}

local wm, sm = nil, nil
local pending = {{}}
local wet0 = false
local ready = false
local last_scene = nil

local rain_cache = {{}}
local targets = {{}}

local ui = {{ wet = 0, status = "等待...", loaded = {{}}, failed = {{}}, swapped = 0, found = 0 }}

local function arr(raw)
    if not raw then return {{}} end
    if type(raw) == "table" then return raw end
    local t = {{}}
    local ok, n = pcall(function() return raw:get_Count() end)
    if ok then for i = 0, n - 1 do local o, m = pcall(function() return raw:get_Item(i) end)
        if o then t[#t+1] = m end end end
    return t
end

re.on_application_entry("BeginRendering", function()
    for _, s in ipairs(pending) do
        pcall(function() s.m:call("setMaterialTexture", s.mi, s.si, s.t) end)
    end
    pending = {{}}
end)

re.on_frame(function()
    if not sm then
        sm = sdk.get_native_singleton("via.SceneManager")
        if not sm then return end
        wm = sdk.get_managed_singleton("chainsaw.WeatherManager")
    end

    -- 检测场景切换，自动重新预加载
    local sc = sdk.call_native_func(sm, sdk.find_type_definition("via.SceneManager"), "get_CurrentScene")
    if sc and last_scene and sc ~= last_scene then
        ready = false; rain_cache = {{}}; targets = {{}}; ui.loaded = {{}}; ui.failed = {{}}; ui.found = 0
    end
    if sc then last_scene = sc end

    if not ready then
        if not sc then return end
        local meshes = arr(sc:call("findComponents(System.Type)", sdk.typeof("via.render.Mesh")))
        local rain_set = {{}}; for _, p in ipairs(SWAP_LIST) do rain_set[p[2]] = true end
        local orig_set = {{}}; for _, p in ipairs(SWAP_LIST) do orig_set[p[1]] = p[2] end
        local hash_fn = sdk.find_type_definition("via.murmur_hash"):get_method("calc32")

        for _, mesh in ipairs(meshes) do
            local mc = mesh:call("get_MaterialNum")
            if mc then for mi = 0, mc - 1 do
                local tc = mesh:call("getMaterialTextureNum", mi)
                if tc then for si = 0, tc - 1 do
                    local tex = mesh:call("getMaterialTexture", mi, si)
                    if tex then
                        local path = tex:call("ToString()"):match("^.+%[@?(.+)%]")
                        if path then
                            if rain_set[path] then
                                rain_cache[path] = tex:add_ref()
                                ui.loaded[#ui.loaded+1] = path
                            elseif orig_set[path] then
                                local sn = mesh:call("getMaterialTextureName", mi, si)
                                local vi = mesh:call("getMaterialVariableIndex", mi, hash_fn:call("calc32", sn or ""))
                                targets[#targets+1] = {{m=mesh, mi=mi, si=(vi~=255)and vi or si, orig=tex:add_ref(), rain=orig_set[path]}}
                                ui.found = ui.found + 1
                            end
                        end
                    end
                end end
            end end
        end

        for _, p in ipairs(SWAP_LIST) do
            if not rain_cache[p[2]] then ui.failed[#ui.failed+1] = p[2] end
        end
        ui.status = string.format("就绪: %d rain贴图, %d 目标, %d 缺失",
            #ui.loaded, ui.found, #ui.failed)
        -- 没找到目标就持续重试，找到了继续往下走（当帧就生效）
        ready = #targets > 0
        if not ready then return end
    end

    local wet = wm and (wm:get_field("_CurrentGlobalWetRate") or 0) or 0
    ui.wet = wet
    if (wet > 0.01) == wet0 then return end
    wet0 = wet > 0.01

    local swapped = 0
    for _, t in ipairs(targets) do
        if wet0 and rain_cache[t.rain] then
            pending[#pending+1] = {{m=t.m, mi=t.mi, si=t.si, t=rain_cache[t.rain]}}
            swapped = swapped + 1
        elseif not wet0 and t.orig then
            pending[#pending+1] = {{m=t.m, mi=t.mi, si=t.si, t=t.orig}}
            swapped = swapped + 1
        end
    end

    ui.swapped = swapped
    ui.status = wet0 and string.format("湿身 替换:%d", swapped) or string.format("干燥 恢复:%d", swapped)
end)

"""

def main():
    print("=" * 56)
    print("  RE4R Rain Texture Swap - Config Generator")
    print("  1) English    2) 中文")
    lang = input("  Select language / 选择语言 (1/2): ").strip()
    is_en = lang == "1"

    T = {
        "title": "RE4R Rain Texture Swap - Config Generator" if is_en else "RE4R 湿身换贴图 - 配置生成器",
        "author": "Generator by: NyaSita" if is_en else "生成器作者: NyaSita",
        "path_note": "Paths must match MDF references" if is_en else "路径需与 MDF 中填写的路径一致",
        "end_hint": "Type cplt to finish" if is_en else "输入 cplt 结束并生成脚本",
        "tex_orig": lambda n: f"Texture {n} - Original: " if is_en else f"贴图{n} 原贴图: ",
        "tex_rain": lambda n: f"Texture {n} - Wet: " if is_en else f"贴图{n} 浸湿贴图: ",
        "empty_err": "Path cannot be empty" if is_en else "路径不能为空",
        "added": lambda o, r: f"  -> Added: {o}  =>  {r}" if is_en else f"  -> 已添加: {o}  =>  {r}",
        "no_input": "No textures entered, exiting." if is_en else "未输入任何贴图，退出。",
        "name_hint": "Suggested: ModName_rain_texture_swap" if is_en else "建议命名: mod名_rain_texture_swap",
        "name_example": "e.g. XiShi_rain_texture_swap" if is_en else "例如: XiShi_rain_texture_swap",
        "name_warn": "Use unique names to avoid mod conflicts" if is_en else "不同 mod 用不同名字，避免冲突",
        "name_prompt": "Script filename (without .lua): " if is_en else "脚本文件名 (不含.lua): ",
        "name_empty": "Cannot be empty" if is_en else "不能为空",
        "name_ascii": "Only English letters and numbers, no spaces" if is_en else "只能用英文和数字，不能有空格",
        "name_exists": lambda n: f"  {n}.lua already exists, pick another name" if is_en else f"  {n}.lua 已存在，换一个名字",
        "done": lambda out, n: f"Generated: {out}\n  {n} texture pairs\n  Place in reframework/autorun/" if is_en else f"已生成: {out}\n  共 {n} 对贴图\n  放入 reframework/autorun/ 即可",
        "cplt": "cplt",
    }

    print("=" * 56)
    print(f"  {T['title']}")
    print(f"  {T['author']}")
    print(f"  {T['path_note']}")
    print(f"  {T['end_hint']}")
    print("=" * 56)
    print()

    pairs = []
    n = 1

    while True:
        orig = input(T["tex_orig"](n)).strip()
        if orig.lower() == T["cplt"]:
            break
        if not orig:
            print(f"  {T['empty_err']}")
            continue

        rain = input(T["tex_rain"](n)).strip()
        if rain.lower() == T["cplt"]:
            break
        if not rain:
            print(f"  {T['empty_err']}")
            continue

        pairs.append((orig, rain))
        print(T["added"](orig, rain))
        print()
        n += 1

    if not pairs:
        print(T["no_input"])
        return

    print()
    print("-" * 56)
    print(f"  {T['name_hint']}")
    print(f"  {T['name_example']}")
    print(f"  {T['name_warn']}")
    print("-" * 56)
    while True:
        name = input(T["name_prompt"]).strip()
        if not name:
            print(f"  {T['name_empty']}")
            continue
        if not name.isascii() or " " in name:
            print(f"  {T['name_ascii']}")
            continue
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".lua")
        if os.path.exists(out):
            print(T["name_exists"](name))
            continue
        break

    path_lines = ",\n".join(
        f'    {{ "{o}", "{r}" }}' for o, r in pairs
    )
    script = TEMPLATE.format(
        paths=path_lines,
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    with open(out, "w", encoding="utf-8") as f:
        f.write(script)

    print()
    print("=" * 56)
    print(T["done"](out, len(pairs)))
    print("=" * 56)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n已取消。")
