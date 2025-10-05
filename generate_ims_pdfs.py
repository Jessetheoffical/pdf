from fpdf import FPDF
import re
import os

PRIMARY = (15, 98, 254)      # #0F62FE
DARK = (22, 28, 36)          # near-black
MUTED = (102, 112, 128)      # gray-500
LIGHT_BG = (245, 247, 250)   # subtle gray background blocks
ACCENT = (124, 58, 237)      # purple accent

FONT_DIR = "fonts"
EN_FONT = os.path.join(FONT_DIR, "DejaVuSans.ttf")
ZH_FONT = os.path.join(FONT_DIR, "NotoSansSC-Regular.otf")  # or SourceHanSansSC-Regular.otf

def check_fonts():
    missing = []
    if not os.path.isfile(EN_FONT):
        missing.append(EN_FONT)
    if not os.path.isfile(ZH_FONT):
        missing.append(ZH_FONT)
    if missing:
        raise FileNotFoundError(
            "Missing font files:\n- " + "\n- ".join(missing) +
            "\nPlease download the fonts and place them under a 'fonts/' directory, or update the paths."
        )

EMOJI_PATTERN = re.compile("[\U00010000-\U0010FFFF]", flags=re.UNICODE)

def strip_emojis(text: str) -> str:
    return EMOJI_PATTERN.sub("", text)

def normalize_newlines(text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t

class StyledPDF(FPDF):
    def __init__(self, lang="EN", title="IMS Hub Ecosystem Master Plan"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.lang = lang
        self.title_text = title
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 16, 18)
        self.alias_nb_pages()
        self._register_fonts()

    def _register_fonts(self):
        self.add_font("EN", "", EN_FONT, uni=True)
        self.add_font("ZH", "", ZH_FONT, uni=True)
        self.add_font("ENB", "", EN_FONT, uni=True)
        self.add_font("ZHB", "", ZH_FONT, uni=True)

    def header(self):
        self.set_y(10)
        self.set_draw_color(*PRIMARY)
        self.set_line_width(0.4)
        self.line(18, 16, self.w - 18, 16)
        self.set_text_color(*MUTED)
        self.set_xy(18, 8)
        self.set_font(self._pick_font(bold=False), size=9)
        self.cell(0, 6, f"{self.title_text} — {self.lang}", align="R", ln=1)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_text_color(*MUTED)
        self.set_font(self._pick_font(), size=9)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def _pick_font(self, bold=False):
        if self.lang == "EN":
            return "ENB" if bold else "EN"
        else:
            return "ZHB" if bold else "ZH"

    def add_cover(self, subtitle="Smart Matching. Global Connections."):  
        self.add_page()
        self.set_fill_color(*PRIMARY)
        self.rect(0, 0, self.w, 50, style="F")
        self.set_xy(18, 18)
        self.set_text_color(255, 255, 255)
        self.set_font(self._pick_font(bold=True), size=24)
        self.cell(0, 12, self.title_text, ln=1)
        self.set_x(18)
        self.set_font(self._pick_font(), size=13)
        self.set_text_color(230, 240, 255)
        self.cell(0, 8, subtitle, ln=1)
        self.set_y(70)
        self._card(
            title="Overview" if self.lang == "EN" else "概览",
            body=("An AI-driven ecosystem connecting people and opportunities "
                  "across education, healthcare, beauty, travel, business and trade."
                  if self.lang == "EN"
                  else "一个由 AI 驱动的生态系统，连接教育、医疗、美容、旅游、商业和贸易领域的人才与机会。")
        )

    def _card(self, title: str, body: str):
        x, y, w = 18, self.get_y(), self.w - 36
        self.set_xy(x, y)
        self.set_fill_color(*LIGHT_BG)
        self.set_draw_color(230, 235, 240)
        self.set_line_width(0.2)
        self.set_font(self._pick_font(bold=True), size=14)
        th = 8
        self.set_font(self._pick_font(), size=11)
        lines = max(1, len(body) // 60)
        box_h = 10 + th + (lines + 2) * 6 + 10
        self.rounded_rect(x, y, w, box_h, 3, style="DF")
        self.set_xy(x + 10, y + 10)
        self.set_text_color(*DARK)
        self.set_font(self._pick_font(bold=True), size=14)
        self.cell(w - 20, th, title, ln=1)
        self.set_xy(x + 10, y + 10 + th + 2)
        self.set_font(self._pick_font(), size=11)
        self.set_text_color(55, 65, 81)
        self.multi_cell(w - 20, 6, body)
        self.ln(6)

    def write_heading(self, text: str):
        text = text.strip()
        if not text:
            return
        x = self.l_margin
        y = self.get_y() + 2
        bar_w, bar_h = 3, 9
        self.set_fill_color(*ACCENT)
        self.rect(x, y, bar_w, bar_h, style="F")
        self.set_xy(x + bar_w + 3, y - 1)
        self.set_text_color(*DARK)
        self.set_font(self._pick_font(bold=True), size=15)
        self.cell(0, bar_h + 2, text, ln=1)
        self.ln(2)

    def write_subheading(self, text: str):
        self.set_text_color(*PRIMARY)
        self.set_font(self._pick_font(bold=True), size=12.5)
        self.multi_cell(0, 6.5, text)
        self.ln(1)

    def write_body(self, text: str):
        self.set_text_color(31, 41, 55)
        self.set_font(self._pick_font(), size=11.3)
        self.multi_cell(0, 6.2, text)

    def write_bullets(self, items):
        self.set_text_color(31, 41, 55)
        self.set_font(self._pick_font(), size=11.3)
        for it in items:
            self.cell(3)
            self.cell(4, 6.2, "•")
            self.multi_cell(0, 6.2, it)
        self.ln(1)

    def render_text(self, text: str):
        text = strip_emojis(normalize_newlines(text))
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        import re as _re
        for p in paragraphs:
            if "\n" in p and any(line.strip().startswith(('-', '•')) for line in p.splitlines()):
                items = [_re.sub(r"^(-|•)\s*", "", line.strip()) for line in p.splitlines() if line.strip()]
                self.write_bullets(items)
                continue
            if (len(p) <= 60) and (p.endswith(":") or p.endswith("：")):
                self.write_subheading(p)
                continue
            if len(p) <= 48 and (
                p.isupper()
                or _re.match(r"^(IMS|Mission|Goal|Strategic Goal|Integration|Ecosystem|Revenue|Global Vision)\b", p, _re.I)
                or _re.match(r"^(IMS|使命|目标|战略目标|整合|生态系统|收益|全球愿景)", p)
            ):
                self.write_heading(p)
                continue
            self.write_body(p)
            self.ln(1)

def create_styled_pdf(text: str, filename: str, lang: str, title: str, subtitle: str):
    pdf = StyledPDF(lang=lang, title=title)
    pdf.add_cover(subtitle=subtitle)
    pdf.add_page()
    pdf.render_text(text)
    pdf.output(filename)

english_text = """🌐 IMS Hub Ecosystem Master Plan
Smart Matching. Global Connections.

🧠 Core: IMS Hub (The Intelligent Matching System)

IMS Hub is the central AI-driven ecosystem connecting people and opportunities across education, healthcare, beauty, business, and trade.

It is the core engine that powers all branches with:

AI Smart Matching
Verification & Compliance Systems
Visa & Legal Assistance
Insurance, Medical & Driving Licence Services
Centralized Data, Marketing & Brand Infrastructure

Mission:
To build the world’s most intelligent platform for connecting people, opportunities, and verified services — all powered by China’s innovation, global reach, and affordability.

🌿 IMS Branches

Each branch has its own focus, social media, and team, but all connect through IMS Hub’s AI system and share the same global vision.

🏫 1. IMS Scholarships
“Empowering Minds. Creating Global Futures.”

Focus: AI-powered education matching — connecting students with universities, scholarships, and internships worldwide.

Key Features:
Smart scholarship and university recommendations
Study visa and documentation support
Internship and job matching for graduates
Verified institutions and programs
Partnership network with global universities

Goal:
To make IMS Scholarships the go-to platform for global education discovery and academic opportunities.

💎 2. IMS Beauty
“Beauty, Innovation, and Confidence.”

Focus: Position China as a global beauty destination — combining aesthetic services, wellness, and tourism.

Key Features:
Verified cosmetic clinics and beauty centers
Beauty tourism packages (treatment + travel)
Brand collaborations and influencer partnerships
Product sourcing from verified Chinese manufacturers
AI matching for ideal services and beauty providers

Strategic Goal:
To attract global clients to China’s advanced beauty and aesthetic industry through technology, affordability, and verified partnerships.

🏥 3. IMS Medical
“Healthy Connections. Smarter Choices.”

Focus: Global healthcare gateway connecting patients with top hospitals and clinics in China.

Key Features:
Verified hospital & clinic network
Medical AI matching based on needs and budget
Teleconsultation and treatment planning
Full medical tourism support (visa, hotels, logistics)
Integration of Modern Medicine + Traditional Chinese Medicine (TCM)
B2B medical supply & equipment connections

Strategic Goal:
To promote China as a trusted medical destination offering world-class treatment, innovation, and cost-effectiveness.

✈️ 4. IMS Travel
“Journey Smarter. Experience More.”

Focus: Global travel system for tourism, study, medical, and business purposes — integrated with all other IMS branches.

Key Features:
AI-matched travel and tourism packages
Visa processing & travel insurance
Business and medical tourism programs
Accommodation, transport, and translation support
Cultural & business experience coordination

Integration:
Works seamlessly with IMS Beauty and IMS Medical to bring clients for health, beauty, and business trips to China.

🛒 5. IMS Products
“Verified Trade. Smart Global Sourcing.”

Focus: Unified platform for global product sourcing, electronics, and manufacturing partnerships, combining B2B and B2C trade.

Key Features:
Verified factories, sellers, and manufacturers
Product & factory verification (licenses, ownership, compliance)
Smart matching between buyers and Chinese suppliers
Logistics, export, and documentation support
Trade show and partnership facilitation
Electronics, machinery, cosmetics, textiles, auto parts, and more

Strategic Goal:
To become the most trusted and intelligent trade gateway for verified Chinese products — helping global buyers source safely, quickly, and confidently.

🚗 6. IMS Automobile
“Drive Smart. Trade Global.”

Focus: International vehicle and mobility platform powered by IMS Hub’s verification system — covering cars, motorcycles, scooters, and other vehicles.

Key Features:
Verified dealers and exporters of cars, motorcycles, scooters, and related vehicles
Vehicle inspection and authenticity reports
Parts and components sourcing for all vehicle types
Import/export and customs documentation
Financing, insurance, and logistics support

Strategic Goal:
To make IMS Automobile the most reliable cross-border platform for vehicles and mobility solutions, enabling safe and efficient international trade.

🧭 Ecosystem Synergy
IMS Branch\tKey Linkages\tIntegration Examples
IMS Beauty\tMedical, Travel\tMedical & beauty tourism to China
IMS Medical\tTravel, Business\tHealth + business visit experiences
IMS Scholarships\tTravel, Business\tStudy, internship, and travel support
IMS Products\tCars, Business\tTrade fairs, manufacturing partnerships
IMS Travel\tAll\tUnified travel, visa, and support services
IMS Hub\tAll\tAI backbone, verification, and shared ecosystem

💼 Revenue Streams
Subscription Plans: Monthly / 6-Month / 12-Month (unlimited access)
Partner Fees: Hospitals, clinics, universities, and factories pay for verified listings
Service Fees: Visa, legal, translation, and logistics support
Commissions: Earnings from completed bookings, partnerships, and placements
Advertising: Sponsored visibility across IMS branches

🌍 Global Vision
IMS Hub aims to become a world-leading AI-powered platform that connects people, businesses, and institutions through trust, intelligence, and opportunity.

By merging education, healthcare, beauty, travel, and trade, IMS Hub will:
Promote China as a top global destination for opportunity and innovation
Build a sustainable international ecosystem for cooperation and growth
Empower people to achieve global goals — all in one intelligent network
"""

chinese_text = """🌐 IMS Hub 生态系统总体规划
智能匹配，全球连接

🧠 核心：IMS Hub（智能匹配系统）

IMS Hub 是一个中央 AI 驱动的生态系统，连接教育、医疗、美容、商业和贸易领域的人才与机会。

它是所有分支的核心引擎，提供：

AI 智能匹配
验证与合规系统
签证与法律援助
保险、医疗及驾照服务
数据集中管理、营销与品牌基础设施

使命：
打造全球最智能的平台，连接人才、机会与经过验证的服务——由中国的创新能力、全球影响力与高性价比驱动。

🌿 IMS 分支

每个分支都有自己的重点、社交媒体和团队，但都通过 IMS Hub 的 AI 系统连接，并共享全球愿景。

🏫 1. IMS 奖学金
“赋能智慧，创造全球未来。”

重点：通过 AI 教育匹配，将学生与全球大学、奖学金和实习机会连接起来。

主要功能：
智能推荐奖学金和大学
提供留学签证与文书支持
毕业生实习和就业匹配
认证教育���构和课程
全球大学合作网络

目标：
使 IMS 奖学金成为全球教育发现与学术机会的首选平台。

💎 2. IMS 美容
“美丽、创新与自信。”

重点：将中国打造为全球美容目的地，结合美容服务、健康与旅游。

主要功能：
认证美容诊所和整形中心
美容旅游套餐（治疗+旅行）
品牌合作与网红推广
从认证制造商采购产品
AI 匹配理想服务和美容提供商

战略目标：
通过技术、性价比和认证合作，将国际客户吸引到中国先进的美容和整形产业。

🏥 3. IMS 医疗
“健康连接，更智能的选择。”

重点：全球医疗门户，连接患者与中国顶级医院和诊所。

主要功能：
认证医院与诊所网络
基于需求和预算的医疗 AI 匹配
远程咨询与治疗规划
全面医疗旅游支持（签证、酒店、物流）
现代医学与中医结合
B2B 医疗设备与供应连接

战略目标：
展示中国作为值得信赖的医疗目的地，提供世界级治疗、创新与高性价比。

✈️ 4. IMS 旅游
“智能出行，尽享体验。”

重点：提供全球旅游系统，支持旅游、学习、医疗和商务出行，与所有 IMS 分支整合。

主要功能：
AI 匹配旅游套餐
签证办理与旅行保险
商务及医疗旅游项目
住宿、交通及翻译支持
文化与商务体验协调

整合：
与 IMS 美容和 IMS 医疗无缝协作，为客户提供健康、美容及商务旅行服务。

🛒 5. IMS 产品
“可信贸易，智能全球采购。”

重点：统一平台，进行全球产品采购、电子产品及制造合作，结合 B2B 与 B2C 贸易。

主要功能：
认证工厂、卖家和制造商
产品与工厂验证（许可证、所有权、合规性）
买家与中国供应商智能匹配
物流、出口及文档支持
展会与合作促进
电子产品、机械、化妆品、纺织品、汽车零部件等

战略目标：
成为最可信赖、最智能的中国产品贸易门户，帮助全球买家安全、高效采购。

🚗 6. IMS 汽车与交通工具
“智能出行，全球交易。”

重点：国际车辆及出行平台，由 IMS Hub 验证系统支持——涵盖汽车、摩托车、电动车及其他交通工具。

主要功能：
认证汽车、摩托车、电动车及其他交通工具的经销商与出口商
车辆检测与真实性报告
各类车辆零部件采购
进出口及海关文档支持
融资、保险及物流服务

战略目标：
打造最可靠的跨境车辆及交通工具交易平台，实现安全高效的国际贸易。

🧭 生态系统协同
IMS 分支\t关键联系\t整合示例
IMS 美容\t医疗、旅游\t医疗与美容旅游
IMS 医疗\t旅游、商务\t健康+商务出行
IMS 奖学金\t旅游、商务\t学习、实习及旅游支持
IMS 产品\t汽车与交通工具、商务\t贸易展、制造合作
IMS 旅游\t所有\t统一的旅行、签证及支持服务
IMS Hub\t所有\tAI 中枢、验证及共享生态系统

💼 收益来源
订阅计划：月度 / 6 个月 / 12 个月（无限制访问）
合作方费用：医院、诊所、大学及工厂支付认证列表费用
服务费：签证、法律、翻译及物流支持
佣金：完成的预订、合作与交易所产生收益
广告：在 IMS 分支进行推广和可见性展示

🌍 全球愿景
IMS Hub 致力于成为全球领先的 AI 驱动平台，通过信任、智能与机会连接人才、企业和机构。

通过整合教育、医疗、美容、旅游和贸易，IMS Hub 将：
推广中国作为全球机会与创新的首选目的地
建设可持续的国际合作生态系统
赋能全球用户，通过一个智能网络实现目标
"""

def main():
    check_fonts()
    create_styled_pdf(
        english_text,
        "IMS_Hub_English.pdf",
        lang="EN",
        title="IMS Hub Ecosystem Master Plan",
        subtitle="Smart Matching. Global Connections."
    )
    create_styled_pdf(
        chinese_text,
        "IMS_Hub_Chinese.pdf",
        lang="ZH",
        title="IMS Hub 生态系统总体规划",
        subtitle="智能匹配，全球连接"
    )
    print("Created: IMS_Hub_English.pdf, IMS_Hub_Chinese.pdf")

if __name__ == "__main__":
    main()