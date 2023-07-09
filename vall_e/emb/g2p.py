import argparse
import random
import string
from functools import cache
from pathlib import Path
from pypinyin import pinyin, Style
import torch
from tqdm import tqdm

# 拼音转音素映射表：420
shengyun2ph_dict = {
    'a': 'aa a',
    'ai': 'aa ai',
    'an': 'aa an',
    'ang': 'aa ang',
    'ao': 'aa ao',
    'ba': 'b a',
    'bai': 'b ai',
    'ban': 'b an',
    'bang': 'b ang',
    'bao': 'b ao',
    'bei': 'b ei',
    'ben': 'b en',
    'beng': 'b eng',
    'bi': 'b i',
    'bian': 'b ian',
    'biao': 'b iao',
    'bie': 'b ie',
    'bin': 'b in',
    'bing': 'b ing',
    'bo': 'b o',
    'bu': 'b u',
    'ca': 'c a',
    'cai': 'c ai',
    'can': 'c an',
    'cang': 'c ang',
    'cao': 'c ao',
    'ce': 'c e',
    'cen': 'c en',
    'ceng': 'c eng',
    'ci': 'c iy',
    'cong': 'c ong',
    'cou': 'c ou',
    'cu': 'c u',
    'cuan': 'c uan',
    'cui': 'c ui',
    'cun': 'c un',
    'cuo': 'c uo',
    'cha': 'ch a',
    'chai': 'ch ai',
    'chan': 'ch an',
    'chang': 'ch ang',
    'chao': 'ch ao',
    'che': 'ch e',
    'chen': 'ch en',
    'cheng': 'ch eng',
    'chi': 'ch ix',
    'chong': 'ch ong',
    'chou': 'ch ou',
    'chu': 'ch u',
    'chuai': 'ch uai',
    'chuan': 'ch uan',
    'chuang': 'ch uang',
    'chui': 'ch ui',
    'chun': 'ch un',
    'chuo': 'ch uo',
    'da': 'd a',
    'dai': 'd ai',
    'dan': 'd an',
    'dang': 'd ang',
    'dao': 'd ao',
    'de': 'd e',
    'dei': 'd ei',
    'deng': 'd eng',
    'di': 'd i',
    'dia': 'd ia',
    'dian': 'd ian',
    'diao': 'd iao',
    'die': 'd ie',
    'ding': 'd ing',
    'diu': 'd iu',
    'dong': 'd ong',
    'dou': 'd ou',
    'du': 'd u',
    'duan': 'd uan',
    'dui': 'd ui',
    'dun': 'd un',
    'duo': 'd uo',
    'e': 'ee e',
    'ei': 'ee ei',
    'en': 'ee en',
    'er': 'ee er',
    'fa': 'f a',
    'fan': 'f an',
    'fang': 'f ang',
    'fei': 'f ei',
    'fen': 'f en',
    'feng': 'f eng',
    'fo': 'f o',
    'fou': 'f ou',
    'fu': 'f u',
    'ga': 'g a',
    'gai': 'g ai',
    'gan': 'g an',
    'gang': 'g ang',
    'gao': 'g ao',
    'ge': 'g e',
    'gei': 'g ei',
    'gen': 'g en',
    'geng': 'g eng',
    'gong': 'g ong',
    'gou': 'g ou',
    'gu': 'g u',
    'gua': 'g ua',
    'guai': 'g uai',
    'guan': 'g uan',
    'guang': 'g uang',
    'gui': 'g ui',
    'gun': 'g un',
    'guo': 'g uo',
    'ha': 'h a',
    'hai': 'h ai',
    'han': 'h an',
    'hang': 'h ang',
    'hao': 'h ao',
    'he': 'h e',
    'hei': 'h ei',
    'hen': 'h en',
    'heng': 'h eng',
    'hong': 'h ong',
    'hou': 'h ou',
    'hu': 'h u',
    'hua': 'h ua',
    'huai': 'h uai',
    'huan': 'h uan',
    'huang': 'h uang',
    'hui': 'h ui',
    'hun': 'h un',
    'huo': 'h uo',
    'yi': 'ii i',
    'ya': 'ii ia',
    'yan': 'ii ian',
    'yang': 'ii iang',
    'yao': 'ii iao',
    'ye': 'ii ie',
    'yin': 'ii in',
    'ying': 'ii ing',
    'yong': 'ii iong',
    'you': 'ii iu',
    'ji': 'j i',
    'jia': 'j ia',
    'jian': 'j ian',
    'jiang': 'j iang',
    'jiao': 'j iao',
    'jie': 'j ie',
    'jin': 'j in',
    'jing': 'j ing',
    'jiong': 'j iong',
    'jiu': 'j iu',
    'ju': 'j v',
    'juan': 'j van',
    'jue': 'j ve',
    'jun': 'j vn',
    'ka': 'k a',
    'kai': 'k ai',
    'kan': 'k an',
    'kang': 'k ang',
    'kao': 'k ao',
    'ke': 'k e',
    'ken': 'k en',
    'keng': 'k eng',
    'kong': 'k ong',
    'kou': 'k ou',
    'ku': 'k u',
    'kua': 'k ua',
    'kuai': 'k uai',
    'kuan': 'k uan',
    'kuang': 'k uang',
    'kui': 'k ui',
    'kun': 'k un',
    'kuo': 'k uo',
    'la': 'l a',
    'lai': 'l ai',
    'lan': 'l an',
    'lang': 'l ang',
    'lao': 'l ao',
    'le': 'l e',
    'lei': 'l ei',
    'leng': 'l eng',
    'li': 'l i',
    'lia': 'l ia',
    'lian': 'l ian',
    'liang': 'l iang',
    'liao': 'l iao',
    'lie': 'l ie',
    'lin': 'l in',
    'ling': 'l ing',
    'liu': 'l iu',
    'lo': 'l o',
    'long': 'l ong',
    'lou': 'l ou',
    'lu': 'l u',
    'luan': 'l uan',
    'lun': 'l un',
    'luo': 'l uo',
    'lv': 'l v',
    'lve': 'l ve',
    'ma': 'm a',
    'mai': 'm ai',
    'man': 'm an',
    'mang': 'm ang',
    'mao': 'm ao',
    'me': 'm e',
    'mei': 'm ei',
    'men': 'm en',
    'meng': 'm eng',
    'mi': 'm i',
    'mian': 'm ian',
    'miao': 'm iao',
    'mie': 'm ie',
    'min': 'm in',
    'ming': 'm ing',
    'miu': 'm iu',
    'mo': 'm o',
    'mou': 'm ou',
    'mu': 'm u',
    'na': 'n a',
    'nai': 'n ai',
    'nan': 'n an',
    'nang': 'n ang',
    'nao': 'n ao',
    'ne': 'n e',
    'nei': 'n ei',
    'nen': 'n en',
    'neng': 'n eng',
    'ni': 'n i',
    'nian': 'n ian',
    'niang': 'n iang',
    'niao': 'n iao',
    'nie': 'n ie',
    'nin': 'n in',
    'ning': 'n ing',
    'niu': 'n iu',
    'nong': 'n ong',
    'nu': 'n u',
    'nuan': 'n uan',
    'nuo': 'n uo',
    'nv': 'n v',
    'nve': 'n ve',
    'o': 'oo o',
    'ou': 'oo ou',
    'pa': 'p a',
    'pai': 'p ai',
    'pan': 'p an',
    'pang': 'p ang',
    'pao': 'p ao',
    'pei': 'p ei',
    'pen': 'p en',
    'peng': 'p eng',
    'pi': 'p i',
    'pian': 'p ian',
    'piao': 'p iao',
    'pie': 'p ie',
    'pin': 'p in',
    'ping': 'p ing',
    'po': 'p o',
    'pou': 'p ou',
    'pu': 'p u',
    'qi': 'q i',
    'qia': 'q ia',
    'qian': 'q ian',
    'qiang': 'q iang',
    'qiao': 'q iao',
    'qie': 'q ie',
    'qin': 'q in',
    'qing': 'q ing',
    'qiong': 'q iong',
    'qiu': 'q iu',
    'qu': 'q v',
    'quan': 'q van',
    'que': 'q ve',
    'qun': 'q vn',
    'ran': 'r an',
    'rang': 'r ang',
    'rao': 'r ao',
    're': 'r e',
    'ren': 'r en',
    'reng': 'r eng',
    'ri': 'r iz',
    'rong': 'r ong',
    'rou': 'r ou',
    'ru': 'r u',
    'ruan': 'r uan',
    'rui': 'r ui',
    'run': 'r un',
    'ruo': 'r uo',
    'sa': 's a',
    'sai': 's ai',
    'san': 's an',
    'sang': 's ang',
    'sao': 's ao',
    'se': 's e',
    'sen': 's en',
    'seng': 's eng',
    'si': 's iy',
    'song': 's ong',
    'sou': 's ou',
    'su': 's u',
    'suan': 's uan',
    'sui': 's ui',
    'sun': 's un',
    'suo': 's uo',
    'sha': 'sh a',
    'shai': 'sh ai',
    'shan': 'sh an',
    'shang': 'sh ang',
    'shao': 'sh ao',
    'she': 'sh e',
    'shei': 'sh ei',
    'shen': 'sh en',
    'sheng': 'sh eng',
    'shi': 'sh ix',
    'shou': 'sh ou',
    'shu': 'sh u',
    'shua': 'sh ua',
    'shuai': 'sh uai',
    'shuan': 'sh uan',
    'shuang': 'sh uang',
    'shui': 'sh ui',
    'shun': 'sh un',
    'shuo': 'sh uo',
    'ta': 't a',
    'tai': 't ai',
    'tan': 't an',
    'tang': 't ang',
    'tao': 't ao',
    'te': 't e',
    'teng': 't eng',
    'ti': 't i',
    'tian': 't ian',
    'tiao': 't iao',
    'tie': 't ie',
    'ting': 't ing',
    'tong': 't ong',
    'tou': 't ou',
    'tu': 't u',
    'tuan': 't uan',
    'tui': 't ui',
    'tun': 't un',
    'tuo': 't uo',
    'wu': 'uu u',
    'wa': 'uu ua',
    'wai': 'uu uai',
    'wan': 'uu uan',
    'wang': 'uu uang',
    'weng': 'uu ueng',
    'wei': 'uu ui',
    'wen': 'uu un',
    'wo': 'uu uo',
    'yu': 'vv v',
    'yuan': 'vv van',
    'yue': 'vv ve',
    'yun': 'vv vn',
    'xi': 'x i',
    'xia': 'x ia',
    'xian': 'x ian',
    'xiang': 'x iang',
    'xiao': 'x iao',
    'xie': 'x ie',
    'xin': 'x in',
    'xing': 'x ing',
    'xiong': 'x iong',
    'xiu': 'x iu',
    'xu': 'x v',
    'xuan': 'x van',
    'xue': 'x ve',
    'xun': 'x vn',
    'za': 'z a',
    'zai': 'z ai',
    'zan': 'z an',
    'zang': 'z ang',
    'zao': 'z ao',
    'ze': 'z e',
    'zei': 'z ei',
    'zen': 'z en',
    'zeng': 'z eng',
    'zi': 'z iy',
    'zong': 'z ong',
    'zou': 'z ou',
    'zu': 'z u',
    'zuan': 'z uan',
    'zui': 'z ui',
    'zun': 'z un',
    'zuo': 'z uo',
    'zha': 'zh a',
    'zhai': 'zh ai',
    'zhan': 'zh an',
    'zhang': 'zh ang',
    'zhao': 'zh ao',
    'zhe': 'zh e',
    'zhei': 'zh ei',
    'zhen': 'zh en',
    'zheng': 'zh eng',
    'zhi': 'zh ix',
    'zhong': 'zh ong',
    'zhou': 'zh ou',
    'zhu': 'zh u',
    'zhua': 'zh ua',
    'zhuai': 'zh uai',
    'zhuan': 'zh uan',
    'zhuang': 'zh uang',
    'zhui': 'zh ui',
    'zhun': 'zh un',
    'zhuo': 'zh uo',
    'cei': 'c ei',
    'chua': 'ch ua',
    'den': 'd en',
    'din': 'd in',
    'eng': 'ee eng',
    'ng': 'ee ng',
    'fiao': 'f iao',
    'yo': 'ii o',
    'kei': 'k ei',
    'len': 'l en',
    'nia': 'n ia',
    'nou': 'n ou',
    'nun': 'n un',
    'rua': 'r ua',
    'tei': 't ei',
    'wong': 'uu uong',
    'n': 'n ng'
}

def convert_to_phonemes(text):
    tmp = pinyin(text, style=Style.TONE3, neutral_tone_with_five=True)
    phonemes = []

    for pp in tmp:
        for p in pp:
            last = p[-1]
            p = p[:-1]
            phoneme = shengyun2ph_dict.get(p, p)
            phoneme_parts = phoneme.split(" ")
            phonemes.append(phoneme_parts[0])

            if len(phoneme_parts) == 2:
                phonemes.append(phoneme_parts[1] + last)

    return phonemes

@cache
def _get_graphs(path):
    with open(path, "r") as f:
        graphs = f.read()
    return graphs


def encode(graphs: str) -> list[str]:
    phones = convert_to_phonemes(graphs)
    ignored = {" ", *string.punctuation}
    return ["_" if p in ignored else p for p in phones]


@torch.no_grad()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--suffix", type=str, default=".normalized.txt")
    args = parser.parse_args()

    paths = list(args.folder.rglob(f"*{args.suffix}"))
    random.shuffle(paths)

    for path in tqdm(paths):
        phone_path = path.with_name(path.stem.split(".")[0] + ".phn.txt")
        if phone_path.exists():
            continue
        graphs = _get_graphs(path)
        phones = encode(graphs)
        with open(phone_path, "w") as f:
            f.write(" ".join(phones))


if __name__ == "__main__":
    main()
