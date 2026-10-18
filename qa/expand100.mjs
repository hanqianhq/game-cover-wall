import fs from "fs";
import https from "https";
import http from "http";
import { URL } from "url";

const existing = JSON.parse(fs.readFileSync("games/manifest.json", "utf8"));
const have = new Set(existing.map((g) => g.id));

const added = [
  { id: "gta5", zh: "GTA5", en: "Grand Theft Auto V", steam: 271590, blurb: "洛圣都自由犯罪模拟器。再抢一辆车就收工。" },
  { id: "portal-2", zh: "传送门2", en: "Portal 2", steam: 620, blurb: "现在请准备好被蛋糕欺骗。科学需要你。" },
  { id: "half-life-alyx", zh: "半条命：阿利克斯", en: "Half-Life: Alyx", steam: 546560, blurb: "VR 里最像电影的射击。重力手套真香。" },
  { id: "doom-eternal", zh: "毁灭战士：永恒", en: "DOOM Eternal", steam: 782330, blurb: "撕碎地狱。配乐比子弹还吵。" },
  { id: "l4d2", zh: "求生之路2", en: "Left 4 Dead 2", steam: 550, blurb: "四人一车，僵尸一海。别放生队友。" },
  { id: "cs2", zh: "反恐精英2", en: "Counter-Strike 2", steam: 730, blurb: "枪法、道具、心态。一局五分钟，一怒一下午。" },
  { id: "pubg", zh: "绝地求生", en: "PUBG: BATTLEGROUNDS", steam: 578080, blurb: "大地图吃鸡鼻祖。决赛圈记得投烟。" },
  { id: "helldivers-2", zh: "绝地潜兵2", en: "HELLDIVERS 2", steam: 553850, blurb: "为了超级地球！友军误伤也是民主的一部分。" },
  { id: "deep-rock", zh: "深岩银河", en: "Deep Rock Galactic", steam: 548430, blurb: "石头！矮人挖矿射击。啤酒与虫潮。" },
  { id: "forza-horizon-5", zh: "极限竞速：地平线5", en: "Forza Horizon 5", steam: 1551360, blurb: "墨西哥开放世界飙车嘉年华。" },
  { id: "rocket-league", zh: "火箭联盟", en: "Rocket League", steam: 252950, blurb: "足球加赛车。空中对着来一脚。" },
  { id: "factorio", zh: "异星工厂", en: "Factorio", steam: 427520, blurb: "自动化上瘾警告。虫子只是插曲。" },
  { id: "satisfactory", zh: "幸福工厂", en: "Satisfactory", steam: 526870, blurb: "第一人称盖厂。传送带美学。" },
  { id: "stellaris", zh: "群星", en: "Stellaris", steam: 281990, blurb: "银河帝国养成。危机到来前先扩边境。" },
  { id: "ck3", zh: "十字军之王3", en: "Crusader Kings III", steam: 1158310, blurb: "中世纪人生模拟器。联姻比打仗重要。" },
  { id: "aoe2", zh: "帝国时代2：决定版", en: "Age of Empires II: Definitive Edition", steam: 813780, blurb: "农民！造农民！经典即时战略回家。" },
  { id: "undertale", zh: "Undertale", en: "Undertale", steam: 391540, blurb: "杀或饶，都是你的选择。配乐永生。" },
  { id: "outer-wilds", zh: "星际拓荒", en: "Outer Wilds", steam: 753640, blurb: "22 分钟一次的宇宙循环。别剧透。" },
  { id: "it-takes-two", zh: "双人成行", en: "It Takes Two", steam: 1426210, blurb: "夫妻档合作神作。一人走不动。" },
  { id: "phasmophobia", zh: "恐鬼症", en: "Phasmophobia", steam: 739630, blurb: "四人探灵。证据不够就别喊名字。" },
  { id: "lethal-company", zh: "致命公司", en: "Lethal Company", steam: 1966720, blurb: "打工捞垃圾。月亮很大，胆子要小。" },
  { id: "sf6", zh: "街头霸王6", en: "Street Fighter 6", steam: 1364780, blurb: "现代格斗入门友好。驱动冲击冲！" },
  { id: "tekken-8", zh: "铁拳8", en: "TEKKEN 8", steam: 1778820, blurb: "三维度连段盛宴。愤怒爆发即帅气。" },
  { id: "death-stranding", zh: "死亡搁浅", en: "Death Stranding", steam: 1190460, blurb: "送快递拯救世界。造路是浪漫。" },
  { id: "horizon-zd", zh: "地平线：零之曙光", en: "Horizon Zero Dawn", steam: 1151640, blurb: "机械恐龙猎人。弓箭与未来神话。" },
  { id: "uncharted", zh: "神秘海域：盗贼遗迹合辑", en: "UNCHARTED: Legacy of Thieves Collection", steam: 1659420, blurb: "电影关卡跳跃。德雷克又掉下去了。" },
  { id: "like-a-dragon", zh: "如龙7：光与暗的去向", en: "Yakuza: Like a Dragon", steam: 1235140, blurb: "春日一番转职 RPG。歌舞伎町最热闹。" },
  { id: "ff7-remake", zh: "最终幻想7 重制版", en: "FINAL FANTASY VII REMAKE INTERGRADE", steam: 1462040, blurb: "米德加再见面。克劳德甩头发。" },
  { id: "p4g", zh: "女神异闻录4黄金版", en: "Persona 4 Golden", steam: 1113000, blurb: "乡下推理与青春。电视里的真相。" },
  { id: "valheim", zh: "英灵神殿", en: "Valheim", steam: 892970, blurb: "维京生存建造。先打鹿，再打神。" },
  { id: "rust", zh: "锈湖？不，Rust", en: "Rust", steam: 252490, blurb: "裸体出生，全服战争。门锁很重要。" },
  { id: "palworld", zh: "幻兽帕鲁", en: "Palworld", steam: 1623730, blurb: "抓宠、造枪、建基地。赛博牧场。" },
  { id: "sons-of-forest", zh: "森林之子", en: "Sons Of The Forest", steam: 1326470, blurb: "荒岛生存。开建豪华木屋。" },
  { id: "among-us", zh: "Among Us", en: "Among Us", steam: 945360, blurb: "谁是内鬼？紧急会议现在开始。" },
  { id: "no-mans-sky", zh: "无人深空", en: "No Man's Sky", steam: 275850, blurb: "宇宙很大。飞、挖、建、交朋友。" },
  { id: "starfield", zh: "星空", en: "Starfield", steam: 1716740, blurb: "又是你，又要登上一颗新星球。" },
  { id: "warframe", zh: "星际战甲", en: "Warframe", steam: 230410, blurb: "忍者空战刷宝。免费但很深。" },
  { id: "apex", zh: "Apex 英雄", en: "Apex Legends", steam: 1172470, blurb: "三排英雄射击。滑铲即正义。" },
  { id: "naraka", zh: "永劫无间", en: "NARAKA: BLADEPOINT", steam: 1203220, blurb: "近战武侠吃鸡。振刀瞬间很帅。" },
  { id: "hades-2", zh: "哈迪斯2", en: "Hades II", steam: 1145350, blurb: "梅利诺厄出征。月光与巫术。" },
  { id: "animal-well", zh: "动物井", en: "Animal Well", steam: 2184270, blurb: "像素秘境探索。鸡蛋与谜题。" },
  { id: "against-storm", zh: "对抗风暴", en: "Against the Storm", steam: 1336490, blurb: "黑暗奇幻城市建设。雨一直下。" },
  { id: "metro-exodus", zh: "地铁：离乡", en: "Metro Exodus", steam: 412020, blurb: "废土列车旅行。防毒面具别忘。" },
  { id: "control", zh: "控制", en: "Control", steam: 870780, blurb: "超能局长上班。建筑会变形。" },
  { id: "re-village", zh: "生化危机8：村庄", en: "Resident Evil Village", steam: 1196590, blurb: "伊森又来了。城堡与狼嚎。" },
  { id: "re2r", zh: "生化危机2：重制版", en: "Resident Evil 2", steam: 883710, blurb: "浣熊市重逢。走廊很窄，子弹很多。" },
  { id: "gow-ragnarok", zh: "战神：诸神黄昏", en: "God of War Ragnarök", steam: 2322010, blurb: "父子再上路。终焉之战将至。" },
  { id: "spider-man-2", zh: "漫威蜘蛛侠2", en: "Marvel's Spider-Man 2", steam: 2651280, blurb: "双蛛侠摆荡纽约。共生体来了。" },
  { id: "tlou2", zh: "最后生还者2", en: "The Last of Us Part II Remastered", steam: 2531310, blurb: "仇恨与循环。故事不会轻松。" },
  { id: "sea-of-thieves", zh: "盗贼之海", en: "Sea of Thieves", steam: 1172620, blurb: "海盗联机。藏宝图与背叛。" },
];

const fresh = added.filter((g) => !have.has(g.id));
console.log("to add", fresh.length);
if (fresh.length !== 50) console.log("WARN expected 50 got", fresh.length);

const all = existing.concat(fresh.map((g) => ({
  ...g,
  file: `${g.id}.jpg`,
  type: "steam-store-art",
  note: undefined,
})));

// keep stylized fields for non-steam from existing
const normalized = all.map((g) => {
  if (g.steam) {
    return { id: g.id, zh: g.zh, en: g.en, steam: g.steam, blurb: g.blurb, file: `${g.id}.jpg`, type: "steam-store-art" };
  }
  return { id: g.id, zh: g.zh, en: g.en, steam: null, blurb: g.blurb, file: g.file || `${g.id}.png`, type: "stylized-placeholder", note: g.note };
});

fs.writeFileSync("games/manifest.json", JSON.stringify(normalized, null, 2) + "\n", "utf8");
console.log("total", normalized.length);

function fetchToFile(url, dest) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const lib = u.protocol === "https:" ? https : http;
    const req = lib.get(url, { headers: { "User-Agent": "visual-lab/1.0" } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        fetchToFile(res.headers.location, dest).then(resolve, reject);
        return;
      }
      if (res.statusCode !== 200) { res.resume(); reject(new Error("HTTP " + res.statusCode)); return; }
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => {
        const buf = Buffer.concat(chunks);
        if (buf.length < 3000) return reject(new Error("small " + buf.length));
        fs.writeFileSync(dest, buf);
        resolve(buf.length);
      });
    });
    req.on("error", reject);
    req.setTimeout(60000, () => { req.destroy(); reject(new Error("timeout")); });
  });
}

const failed = [];
for (let i = 0; i < fresh.length; i += 5) {
  const batch = fresh.slice(i, i + 5);
  await Promise.all(batch.map(async (g) => {
    const dest = `public/covers/${g.id}.jpg`;
    if (fs.existsSync(dest) && fs.statSync(dest).size > 3000) {
      console.log("skip", g.id);
      return;
    }
    const urls = [
      `https://cdn.cloudflare.steamstatic.com/steam/apps/${g.steam}/library_600x900_2x.jpg`,
      `https://cdn.cloudflare.steamstatic.com/steam/apps/${g.steam}/library_600x900.jpg`,
    ];
    let ok = false;
    for (const url of urls) {
      try {
        const n = await fetchToFile(url, dest);
        console.log("ok", g.id, n);
        ok = true;
        break;
      } catch (e) {
        console.log("fail", g.id, e.message);
      }
    }
    if (!ok) failed.push(g.id);
  }));
}
console.log("FAILED", failed.join(",") || "none");
fs.writeFileSync("qa/added-ids.json", JSON.stringify({ added: fresh.map(g=>g.id), failed, categories: [
  "射击/吃鸡/联机对抗",
  "竞速/体育",
  "模拟经营/4X/工厂",
  "叙事独立/解谜",
  "恐怖合作",
  "格斗",
  "主机3A移植",
  "JRPG/如龙/最终幻想",
  "生存建造",
  "国风近战吃鸡",
] }, null, 2));
