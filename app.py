import gradio as gr
from firefly import FireFly
import copy
import math

def calculate(
        ff_clothes: str, ff_shoes: str, ff_ball: str, ff_rope: str,
        ff_isO2: bool, ff_isO4: bool, ff_isI2: bool, ff_isE1: bool, ff_isWM: bool,
        ff_atk_entry: int, ff_crit_rate_entry: int, ff_crit_dmg_entry: int, ff_break_entry: int,
        is_rm_skill: bool, rm_break: float, is_rm_ultimate: bool,
        is_rm_e1: bool, is_rm_e2: bool, is_rm_lc: bool,
        hh_crit_dmg: float, is_hh_skill: bool, is_hh_ultimate: bool,
        is_hh_e1: bool, is_hh_e2: bool, is_hh_lc: bool,
        is_tb_ultimate: bool, is_tb_tech: bool, num_enemy: int, tb_break_eff: float, is_tb_e4: bool,
        is_fx_skill: bool, is_fx_e1: bool, break_status: bool
) -> tuple:

    ff = FireFly()
    ff.clothes_select(ff_clothes)
    ff.shoes_select(ff_shoes)
    ff.ball_select(ff_ball)
    ff.rope_select(ff_rope)

    ff.entry_atk(ff_atk_entry)
    ff.entry_crit_rate(ff_crit_rate_entry)
    ff.entry_crit_dmg(ff_crit_dmg_entry)
    ff.entry_break_eff(ff_break_entry)

    if ff_isO2:
        ff.outer_two()
    if ff_isI2:
        ff.inner_two()

    if ff_isE1:
        ff.e1()
    if ff_isWM:
        ff.watchmaker()

    ff.break_from_atk()

    if break_status:
        break_status_multiplier = 1
        ff.break_status()
    else:
        break_status_multiplier = 0.9

    ff_team = copy.deepcopy(ff)
    ff_team = apply_ruan_mei(ff_team, break_status, is_rm_skill, rm_break, 
                               is_rm_ultimate, is_rm_e1, is_rm_e2, is_rm_lc)
    ff_team = apply_sparkle(ff_team, hh_crit_dmg, is_hh_skill, is_hh_ultimate, is_hh_lc, is_hh_e1, is_hh_e2)
    ff_team = apply_fu_xuan(ff_team, is_fx_skill, is_fx_e1)
    ff_team = apply_trailblazer(ff_team, is_tb_ultimate, is_tb_tech, num_enemy, tb_break_eff, is_tb_e4)

    if ff_isO4:
        ff.outer_four()
        ff_team.outer_four()
    
    ff.multiple_from_break()
    ff.def_dec_from_break()
    ff_team.multiple_from_break()
    ff_team.def_dec_from_break()
    
    direct_def_multiplier = min(1, 1000 / (1000 + 1000 * (1 - ff_team.def_dec_all)))
    direct_dmg_center = ff_team.char_atk * ff_team.multiple_center * \
        ff_team.crit_rate * (1 + ff_team.crit_dmg) * \
        (1 + ff_team.dmg_enhance) * (1 + ff_team.dmg_weakness) * \
        (1 + ff_team.res_pen) * direct_def_multiplier * break_status_multiplier
    direct_dmg_adj = direct_dmg_center / 2
    direct_dmg_tot = 2 * direct_dmg_center

    if is_rm_skill:
        toughness_reduction = 6
    else:
        toughness_reduction = 4.5

    break_def_multiplier = min(1,
        1000 / (1000 + 1000 * (1 - (ff_team.def_dec_break + ff_team.def_dec_all))))
    super_break_dmg = 3768 * toughness_reduction * (1 + ff_team.break_eff) * ff_team.super_break * \
        break_def_multiplier * (1 + ff_team.dmg_weakness) * (1 + ff_team.res_pen)
    super_break_dmg_adj = super_break_dmg / 2
    super_break_dmg_tot = 2 * super_break_dmg
        

    return (
        ff.char_atk, ff.crit_rate, ff.crit_dmg, ff.multiple_center, ff.multiple_adj, ff.break_eff,
        ff_team.char_atk, ff_team.crit_rate, ff_team.crit_dmg, ff_team.multiple_center, ff_team.multiple_adj, ff_team.break_eff,
        ff_team.dmg_enhance, ff_team.dmg_weakness, ff_team.res_pen, ff_team.def_dec_all, ff_team.def_dec_break,
        direct_dmg_center, direct_dmg_adj, direct_dmg_tot, direct_def_multiplier,
        break_def_multiplier, super_break_dmg, super_break_dmg_adj, super_break_dmg_tot
    )


def apply_ruan_mei(ff: FireFly, break_status: bool,
        is_rm_skill: bool, rm_break: float, is_rm_ultimate: bool,
        is_rm_e1: bool, is_rm_e2: bool, is_rm_lc: bool
) -> FireFly:
    ff.break_eff += 0.2
    if is_rm_skill:
        ff.dmg_enhance += (0.32 + max(0.06 * math.floor((rm_break*100-120) / 10), 0.36))
    if is_rm_ultimate:
        ff.res_pen += 0.25
    if is_rm_e1:
        ff.def_dec_all += 0.2
    if is_rm_e2 and break_status:
        ff.dmg_enhance += 0.4
    if is_rm_lc:
        ff.dmg_enhance += 0.24
    
    return ff


def apply_sparkle(ff: FireFly, hh_crit_dmg: float,
        is_hh_skill: bool, is_hh_ultimate: bool, is_hh_lc: bool,
        is_hh_e1: bool, is_hh_e2: bool) -> FireFly:
    if is_hh_skill:
        ff.crit_dmg += (0.24 + 0.45 * hh_crit_dmg)
    if is_hh_ultimate:
        ff.dmg_enhance += 0.48
    if is_hh_e1:
        ff.char_atk += ff.effect_atk * 0.4
    if is_hh_e2:
        ff.def_dec_all += 0.24
    if is_hh_lc:
        ff.crit_rate += 0.1
        ff.crit_dmg += 0.28
    return ff

def apply_trailblazer(ff: FireFly, is_tb_ultimate: bool, is_tb_tech: bool, num_enemy: int,
        tb_break_eff: float, is_tb_e4: bool) -> FireFly:
    if is_tb_ultimate:
        ff.break_eff += 0.3
    if is_tb_tech:
        ff.break_eff += 0.3
    match num_enemy:
        case 1:
            ff.super_break += 1.6
        case 2:
            ff.super_break += 1.5
        case 3:
            ff.super_break += 1.4
        case 4:
            ff.super_break += 1.3
        case _:
            ff.super_break += 1.2
    if is_tb_e4:
        ff.break_eff += tb_break_eff * 0.15
    return ff


def apply_fu_xuan(ff: FireFly, is_fx_skill: bool, is_fx_e1: bool) -> FireFly:
    if is_fx_skill:
        ff.crit_rate += 0.12
    if is_fx_e1:
        ff.crit_dmg += 0.3
    return ff


# Define the layout of the UI
with gr.Blocks() as demo:
    gr.Markdown("# 流萤输出计算器")

    ffdata = dict(); ttdata = dict(); indata = dict()

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 流萤本体数值")
            ff_atk = gr.Textbox(label="攻击力: ")
            ff_crit_rate = gr.Textbox(label="暴击率: ")
            ff_crit_dmg = gr.Textbox(label="暴击伤害: ")
            ff_m_center = gr.Textbox(label="中心伤害倍率: ")
            ff_m_adj = gr.Textbox(label="扩散伤害倍率: ")
            ff_break = gr.Textbox(label="击破特攻: ")

        with gr.Column():
            gr.Markdown("### 遗器主词条")
            ff_clothes = gr.Radio(
                label="衣服主词条",
                choices=["攻击衣", "暴击衣"],
                value="暴击衣"
            )
            ff_shoes = gr.Radio(
                label="鞋子主词条",
                choices=["攻击鞋", "速度鞋"],
                value="攻击鞋"
            )
            ff_ball = gr.Radio(
                label="球主词条",
                choices=["火伤球", "攻击球"],
                value="攻击球"
            )
            ff_rope = gr.Radio(
                label="绳子主词条",
                choices=["攻击绳", "击破绳"],
                value="击破绳"
            )
            ff_isO2 = gr.Checkbox(label="是否激活外圈2件套", value=True)
            ff_isO4 = gr.Checkbox(label="是否激活外圈4件套", value=True)
            ff_isI2 = gr.Checkbox(label="是否激活内圈2件套", value=True)
            ff_isE1 = gr.Checkbox(label="是否激活星魂1", value=True)
            ff_isWM = gr.Checkbox(label="是否激活钟表匠套装效果", value=True)

        with gr.Column():
            gr.Markdown("### 遗器副词条个数")
            ff_atk_entry = gr.Number(label="攻击力: ", value=9)
            ff_crit_rate_entry = gr.Number(label="暴击率: ", value=13)
            ff_crit_dmg_entry = gr.Number(label="暴击伤害: ", value=8)
            ff_break_entry = gr.Number(label="击破特攻: ", value=0)


    gr.Markdown("## 流萤配队：阮梅、花火、同谐主、符玄")
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 阮梅面板自定义")
            rm_break = gr.Number(label="击破特攻", value=1.6)
            is_rm_skill = gr.Checkbox(label="是否激活战技", value=True)
            is_rm_ultimate = gr.Checkbox(label="是否激活终结技", value=True)
            is_rm_e1 = gr.Checkbox(label="是否激活星魂1", value=True)
            is_rm_e2 = gr.Checkbox(label="是否激活星魂2", value=True)
            is_rm_lc = gr.Checkbox(label="是否激活光锥", value=True)
        
        with gr.Column():
            gr.Markdown("### 花火面板自定义")
            hh_crit_dmg = gr.Number(label="暴击伤害", value=2.5)
            is_hh_skill = gr.Checkbox(label="是否激活战技", value=True)
            is_hh_ultimate = gr.Checkbox(label="是否激活终结技", value=True)
            is_hh_e1 = gr.Checkbox(label="是否激活星魂1", value=True)
            is_hh_e2 = gr.Checkbox(label="是否激活星魂2", value=True)
            is_hh_lc = gr.Checkbox(label="是否激活光锥", value=True)
        
        with gr.Column():
            gr.Markdown("### 同谐主面板自定义")
            tb_break_eff = gr.Number(label="击破特攻", value=1.6)
            num_enemy = gr.Number(label="敌人数量", value=1)
            is_tb_ultimate = gr.Checkbox(label="是否激活终结技", value=False)
            is_tb_tech = gr.Checkbox(label="是否激活秘技", value=False)
            is_tb_e4 = gr.Checkbox(label="是否激活星魂4", value=False)

        with gr.Column():
            gr.Markdown("### 符玄面板自定义")
            is_fx_skill = gr.Checkbox(label="是否激活穷观阵", value=True)
            is_fx_e1 = gr.Checkbox(label="是否激活星魂1", value=True)


    gr.Markdown("## 最终流萤输出计算结果")
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 流萤面板")
            ff_direct_atk = gr.Textbox(label="攻击力: ")
            ff_direct_crit_rate = gr.Textbox(label="暴击率: ")
            ff_direct_crit_dmg = gr.Textbox(label="暴击伤害: ")
            ff_direct_m_center = gr.Textbox(label="中心伤害倍率: ")
            ff_direct_m_adj = gr.Textbox(label="扩散伤害倍率: ")
            ff_direct_break = gr.Textbox(label="击破特攻: ")
            ff_direct_dmg_enhance = gr.Textbox(label="增伤: ")
            ff_direct_dmg_weakness = gr.Textbox(label="易伤: ")
            ff_direct_res_pen = gr.Textbox(label="抗性穿透: ")
            ff_direct_def_dec_all = gr.Textbox(label="无条件减防: ")
            ff_direct_def_dec_break = gr.Textbox(label="击破减防: ")
    
        with gr.Column():
            gr.Markdown("### 直伤贡献")
            break_status = gr.Checkbox(label="敌方是否处于击破状态", value=False)
            direct_def_multiplier = gr.Textbox(label="无条件减防: ")
            direct_dmg_center = gr.Textbox(label="中心伤害: ")
            direct_dmg_adj = gr.Textbox(label="扩散伤害: ")
            direct_dmg_tot = gr.Textbox(label="总伤害: ")

            gr.Markdown("### 超级破贡献")
            break_def_multiplier = gr.Textbox(label="击破减防: ")
            super_break_dmg = gr.Textbox(label="超击破伤害: ")
            super_break_dmg_adj = gr.Textbox(label="超击破扩散伤害: ")
            super_break_dmg_tot = gr.Textbox(label="超击破总伤害: ")

    # Button to trigger computation
    compute_button = gr.Button("开始计算")

    # Define the action on button click
    compute_button.click(
        calculate,
        inputs = [
            ff_clothes, ff_shoes, ff_ball, ff_rope,
            ff_isO2, ff_isO4, ff_isI2, ff_isE1, ff_isWM,
            ff_atk_entry, ff_crit_rate_entry, ff_crit_dmg_entry, ff_break_entry,
            is_rm_skill, rm_break, is_rm_ultimate,
            is_rm_e1, is_rm_e2, is_rm_lc,
            hh_crit_dmg, is_hh_skill, is_hh_ultimate,
            is_hh_e1, is_hh_e2, is_hh_lc,
            is_tb_ultimate, is_tb_tech, num_enemy, tb_break_eff, is_tb_e4,
            is_fx_skill, is_fx_e1, break_status
        ],
        outputs = [
            ff_atk, ff_crit_rate, ff_crit_dmg, ff_m_center, ff_m_adj, ff_break,
            ff_direct_atk, ff_direct_crit_rate, ff_direct_crit_dmg, ff_direct_m_center, ff_direct_m_adj, ff_direct_break,
            ff_direct_dmg_enhance, ff_direct_dmg_weakness, ff_direct_res_pen, ff_direct_def_dec_all, ff_direct_def_dec_break,
            direct_dmg_center, direct_dmg_adj, direct_dmg_tot, direct_def_multiplier,
            break_def_multiplier, super_break_dmg, super_break_dmg_adj, super_break_dmg_tot
        ]
    ) # type: ignore

# Launch the Gradio interface
demo.launch()
