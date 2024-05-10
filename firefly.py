import math

class FireFly:

    def __init__(self) -> None:

        self.base_atk = 756.76      # 基础攻击力
        self.lightcone_atk = 635    # 光锥攻击力
        self.effect_atk = self.base_atk + self.lightcone_atk
        self.hand_atk = 352.7       # 手部攻击力
        self.char_atk = self.base_atk + self.lightcone_atk + \
            self.hand_atk           # 初步面板攻击力

        self.crit_rate = 0.05    # 基础暴击率
        self.crit_dmg = 0.5      # 基础暴击伤害

        self.base_multiple_center = 4   # 中心倍率
        self.base_multiple_adj = 2      # 扩散倍率
        self.multiple_from_break_center = 0.5   # 击破转模中心倍率
        self.multiple_from_break_adj = 0.25     #击破转模扩散倍率
        self.multiple_center = self.base_multiple_center
        self.multiple_adj = self.base_multiple_adj

        self.dmg_enhance = 0.        # 增伤
        self.dmg_weakness = 0.       # 易伤
        self.res_pen = 0.            # 抗穿
        self.def_dec_all = 0.        # 无条件减防
        self.def_dec_break = 0.      # 击破减防

        self.trace_break = 0.373            # 击破强化
        self.lightcone_break = 0.6          # 光锥击破
        self.break_eff = self.trace_break + \
            self.lightcone_break            # 击破特攻

        self.article_atk = 0.432            # 主词条攻击
        self.article_dmg_enh = 0.3888       # 主词条增伤
        self.article_break = 0.648          # 主词条击破
        self.article_crit_rate = 0.324      # 主词条暴击率

        self.super_break = 0.               # 超击破倍率


    def clothes_select(self, selection) -> None:
        match selection:
            case "攻击衣":
                self.char_atk += self.effect_atk * self.article_atk
            case "暴击衣":
                self.crit_rate += self.article_crit_rate

    def shoes_select(self, selection) -> None:
        match selection:
            case "攻击鞋":
                self.char_atk += self.effect_atk * self.article_atk
            case "速度鞋":
                pass

    def ball_select(self, selection) -> None:
        match selection:
            case "火伤球":
                self.dmg_enhance += self.article_dmg_enh
            case "攻击球":
                self.char_atk += self.effect_atk * self.article_atk

    def rope_select(self, selection) -> None:
        match selection:
            case "攻击绳":
                self.char_atk += self.effect_atk * self.article_atk
            case "击破绳":
                self.break_eff += self.article_break

    def outer_two(self):
        self.break_eff += 0.16

    def outer_four(self):
        if (self.break_eff >= 1.5) and (self.break_eff < 2.5):
            self.def_dec_break += 0.1
        elif self.break_eff >= 2.5:
            self.def_dec_break += 0.18
        else:
            pass

    def inner_two(self):
        self.break_eff += 0.4

    def e1(self):
        self.def_dec_all += 0.15

    def watchmaker(self):
        self.break_eff += 0.3

    def break_status(self):
        self.dmg_weakness += 0.12
        self.dmg_weakness += 0.15

    def entry_atk(self, atk_cnt) -> None:
        self.char_atk += self.effect_atk * 0.0389 * atk_cnt

    def entry_crit_rate(self, crit_rate_cnt) -> None:
        self.crit_rate += 0.0292 * crit_rate_cnt

    def entry_crit_dmg(self, crit_dmg_cnt) -> None:
        self.crit_dmg += 0.0583 * crit_dmg_cnt

    def entry_break_eff(self, break_eff_cnt) -> None:
        self.break_eff += 0.0583 * break_eff_cnt

    # beta module
    def break_from_atk(self) -> None:
        self.break_eff += max(0.06 * math.floor((self.char_atk - 2400) / 100), 0.6)

    # skill
    def multiple_from_break(self) -> None:
        self.multiple_center = self.base_multiple_center + \
            self.multiple_from_break_center * self.break_eff
        self.multiple_adj = self.base_multiple_adj + \
            self.multiple_from_break_adj * self.break_eff
        
    # gamma module
    def def_dec_from_break(self) -> None:
        if (self.break_eff >= 2.5) and (self.break_eff < 3.6):
            self.def_dec_all += 0.3
        elif self.break_eff >= 3.6:
            self.def_dec_all += 0.4
        else:
            pass

    

