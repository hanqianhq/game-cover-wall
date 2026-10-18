# -*- coding: utf-8 -*-
"""Expand library 100 -> 150, add miHoYo/二游, assign vibes, sync cardTexture + covers."""
from __future__ import annotations
import json, ssl, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass")
COVER_DIR = ROOT / "public" / "covers"
CTX = ssl.create_default_context()

# Existing vibe map (same as before) + new
VIBES = {
  "dave-diver": "cozy", "stardew": "cozy", "terraria": "cozy", "celeste": "cozy",
  "undertale": "cozy", "animal-well": "cozy", "minecraft": "cozy", "sims4": "cozy",
  "pvz": "cozy", "among-us": "cozy", "balatro": "cozy", "hades": "cozy", "hades-2": "cozy",
  "it-takes-two": "cozy", "botw": "cozy", "totk": "cozy", "subnautica": "cozy",
  "outer-wilds": "cozy", "sea-of-thieves": "cozy", "dont-starve": "cozy",
  "against-storm": "cozy", "valheim": "cozy", "palworld": "cozy", "portal-2": "cozy",
  "slay-the-spire": "cozy",
  "cyberpunk-2077": "neon", "control": "neon", "warframe": "neon", "apex": "neon",
  "death-stranding": "neon", "no-mans-sky": "neon", "starfield": "neon",
  "half-life-alyx": "neon",
  "elden-ring": "souls", "sekiro": "souls", "ds3": "souls", "hollow-knight": "souls",
  "silksong": "souls", "nier-automata": "souls",
  "tekken-8": "arcade", "sf6": "arcade", "helldivers-2": "arcade", "doom-eternal": "arcade",
  "dmc5": "arcade", "rocket-league": "arcade", "cs2": "arcade", "pubg": "arcade",
  "l4d2": "arcade", "forza-horizon-5": "arcade", "deep-rock": "arcade", "naraka": "arcade",
  "vampire-survivors": "arcade", "dead-cells": "arcade", "isaac": "arcade",
  "lethal-company": "arcade", "phasmophobia": "arcade", "rust": "arcade",
  "sons-of-forest": "arcade",
  "rdr2": "epic", "witcher-3": "epic", "baldurs-gate-3": "epic", "skyrim": "epic",
  "fallout-4": "epic", "hogwarts": "epic", "kcd2": "epic", "black-myth-wukong": "epic",
  "mhw": "epic", "mh-wilds": "epic", "gow": "epic", "gow-ragnarok": "epic",
  "ghost-of-tsushima": "epic", "uncharted": "epic", "ff7-remake": "epic",
  "spiderman": "epic", "spider-man-2": "epic", "tlou1": "epic", "tlou2": "epic",
  "horizon-zd": "epic", "re-village": "epic", "re2r": "epic", "re4r": "epic",
  "metro-exodus": "epic", "like-a-dragon": "epic", "detroit": "epic", "p5r": "epic",
  "p4g": "epic", "disco-elysium": "epic", "civ6": "epic", "bannerlord": "epic",
  "cities-skylines": "epic", "rimworld": "epic", "dyson-sphere": "epic", "tww3": "epic",
  "factorio": "epic", "satisfactory": "epic", "stellaris": "epic", "ck3": "epic",
  "aoe2": "epic", "gta5": "epic", "dos2": "epic",
}

# 50 new games — miHoYo/二游 first, then fillers
NEW = [
  # —— miHoYo / HoYoverse / peer 二游 ——
  {"id": "genshin", "zh": "原神", "en": "Genshin Impact", "steam": None,
   "blurb": "提瓦特自由旅行。风、岩、雷，抽卡与登山。", "vibe": "neon",
   "placeholder": True, "note": "HoYoverse · stylized placeholder（无 Steam 竖版封面）"},
  {"id": "star-rail", "zh": "崩坏：星穹铁道", "en": "Honkai: Star Rail", "steam": None,
   "blurb": "银河列车下一站。回合制也能很燃。", "vibe": "neon",
   "placeholder": True, "note": "HoYoverse · stylized placeholder"},
  {"id": "zzz", "zh": "绝区零", "en": "Zenless Zone Zero", "steam": 4162040,
   "blurb": "新艾利都委托日。邦布与代理人一起钻空洞。", "vibe": "neon"},
  {"id": "honkai-3rd", "zh": "崩坏3", "en": "Honkai Impact 3rd", "steam": 1671200,
   "blurb": "女武神出击。崩坏与羁绊的三连斩。", "vibe": "arcade"},
  {"id": "wuthering-waves", "zh": "鸣潮", "en": "Wuthering Waves", "steam": 3513350,
   "blurb": "漂泊者苏醒。索拉里斯上的回响与同行。", "vibe": "neon"},
  {"id": "reverse-1999", "zh": "重返未来：1999", "en": "Reverse: 1999", "steam": 3092660,
   "blurb": "暴雨倒转时光。神秘学与二十世纪拼贴。", "vibe": "cozy"},
  {"id": "pgr", "zh": "战双帕弥什", "en": "Punishing: Gray Raven", "steam": 4125930,
   "blurb": "构造体三消连招。科幻废土上的高速刀光。", "vibe": "arcade"},
  {"id": "nikke", "zh": "胜利女神：妮姬", "en": "Goddess of Victory: NIKKE", "steam": 3596190,
   "blurb": "回收地球的枪械少女。纵版射击与剧情双重暴击。", "vibe": "neon"},
  {"id": "blue-archive", "zh": "蔚蓝档案", "en": "Blue Archive", "steam": 3557620,
   "blurb": "基沃托斯的日常与突击。老师请签到。", "vibe": "cozy"},
  {"id": "arknights-endfield", "zh": "明日方舟：终末地", "en": "Arknights: Endfield", "steam": 4732690,
   "blurb": "方舟宇宙工矿开拓。塔防基因遇上工厂节奏。", "vibe": "epic"},
  # —— more fillers (Steam-first) ——
  {"id": "lies-of-p", "zh": "P的谎言", "en": "Lies of P", "steam": 1627720,
   "blurb": "匹诺曹说谎会变长鼻子。魂系木偶巴黎。", "vibe": "souls"},
  {"id": "armored-core-6", "zh": "装甲核心6：境界天火", "en": "ARMORED CORE VI FIRES OF RUBICON", "steam": 1888160,
   "blurb": "组装机体，坠往火线。From 的机甲魂。", "vibe": "souls"},
  {"id": "remnant-2", "zh": "遗迹2", "en": "Remnant II", "steam": 1282100,
   "blurb": "枪械魂系联机。世界随机，Boss 不随机凶。", "vibe": "souls"},
  {"id": "dragons-dogma-2", "zh": "龙之信条2", "en": "Dragon's Dogma 2", "steam": 2054970,
   "blurb": "爪牙同行开放世界。坠落与抓举物理仍是本体。", "vibe": "epic"},
  {"id": "alan-wake-2", "zh": "心灵杀手2", "en": "Alan Wake 2", "steam": 1937780?,
   "blurb": "恐怖与叙事双重曝光。手电筒就是武器。", "vibe": "epic"},
]
