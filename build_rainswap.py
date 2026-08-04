#!/usr/bin/env python3
"""RE4R 湿身换贴图 - 配置生成器 | Author: NyaSita"""

import os
from datetime import datetime

TEMPLATE = r"""--============================================================
-- RE4R 湿身换贴图
-- Author: NyaSita
-- 生成时间: {time}
--============================================================

local SWAP_LIST = {{
{paths}
}}

local wm, sm = nil, nil
local pending = {{}}
local wet0 = false
local ready = false

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

    if not ready then
        local sc = sdk.call_native_func(sm, sdk.find_type_definition("via.SceneManager"), "get_CurrentScene")
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
        ready = true; return
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

re.on_draw_ui(function()
    if imgui.begin_window("RainSwap") then
        imgui.text("状态: " .. ui.status)
        imgui.text(string.format("浸湿度: %.3f", ui.wet))
        imgui.separator()
        if #ui.loaded > 0 then
            imgui.text_colored("Rain贴图:", 0xFF00FF00)
            for _, l in ipairs(ui.loaded) do imgui.text("  " .. l) end
        end
        if #ui.failed > 0 then
            imgui.text_colored("缺失:", 0xFF4444FF)
            for _, f in ipairs(ui.failed) do imgui.text("  " .. f) end
        end
        if #ui.loaded == 0 and #ui.failed == 0 then
            imgui.text_colored("等待场景加载...", 0xFF888888)
        end
        imgui.end_window()
    end
end)
"""

def main():
    print("=" * 56)
    print("  RE4R 湿身换贴图 - 配置生成器")
    print("  Author: NyaSita")
    print("  路径需与 MDF 中填写的路径一致")
    print("  输入 cplt 结束并生成脚本")
    print("=" * 56)
    print()

    pairs = []
    n = 1

    while True:
        orig = input(f"法线{n} 原贴图: ").strip()
        if orig.lower() == "cplt":
            break
        if not orig:
            print("  路径不能为空")
            continue

        rain = input(f"法线{n} 浸湿贴图: ").strip()
        if rain.lower() == "cplt":
            break
        if not rain:
            print("  路径不能为空")
            continue

        pairs.append((orig, rain))
        print(f"  -> 已添加: {orig}  =>  {rain}")
        print()
        n += 1

    if not pairs:
        print("未输入任何贴图，退出。")
        return

    # 输入文件名
    print()
    print("-" * 56)
    print("  建议命名: mod名_rain_texture_swap")
    print("  例如: XiShi_rain_texture_swap")
    print("  不同 mod 用不同名字，避免冲突")
    print("-" * 56)
    while True:
        name = input("脚本文件名 (不含.lua): ").strip()
        if not name:
            print("  不能为空")
            continue
        if not name.isascii() or " " in name:
            print("  只能用英文和数字，不能有空格")
            continue
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".lua")
        if os.path.exists(out):
            print(f"  {name}.lua 已存在，换一个名字")
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
    print(f"  已生成: {out}")
    print(f"  共 {len(pairs)} 对贴图")
    print(f"  放入 reframework/autorun/ 即可")
    print("=" * 56)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n已取消。")
