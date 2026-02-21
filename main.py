import asyncio
import pygame
import pygame_gui
import os
import sys
import random
import datetime
import json
from pygame_gui.core import ObjectID

# Check for Pyodide specific libraries
try:
    from pyodide.http import pyfetch
    IS_WEB = True
except ImportError:
    IS_WEB = False

if not IS_WEB:
    try:
        import aiohttp
    except ImportError:
        print("Warning: aiohttp not found. LLM features may not work on desktop.")
        aiohttp = None

# --- Constants & Configuration ---

# Colors
COLOR_BACKGROUND_DARK = pygame.Color("#0A0A0A")
COLOR_BACKGROUND_WIDGET = pygame.Color("#151515")
COLOR_BACKGROUND_HEADER = pygame.Color("#252525")
COLOR_BACKGROUND_BUTTON = pygame.Color("#383838")
COLOR_BACKGROUND_BUTTON_HOVER = pygame.Color("#4A4A4A")
COLOR_BACKGROUND_BUTTON_PRESSED = pygame.Color("#2F2F2F")
COLOR_BACKGROUND_BUTTON_DISABLED = pygame.Color("#404040")

COLOR_TEXT_GREEN = pygame.Color("#00FF00")
COLOR_TEXT_AMBER = pygame.Color("#FFB000")
COLOR_TEXT_RED = pygame.Color("#FF5555")
COLOR_TEXT_GREY = pygame.Color("#CCCCCC")
COLOR_TEXT_DARK_GREY = pygame.Color("#999999")
COLOR_TEXT_WHITE = pygame.Color("#FFFFFF")

FONT_PATH = "./neodgm_code.ttf"

# Localization Data
TRANSLATIONS = {
    'WINDOW_TITLE':           {'en': "Cognito - AURA Interface", 'ko': "코그니토 - AURA 인터페이스"},
    'SEND_BTN':               {'en': "Send", 'ko': "전송"},
    'INPUT_PLACEHOLDER':      {'en': "Enter your prompt here...", 'ko': "프롬프트를 여기에 입력하세요..."},
    'TIMER_PREFIX':           {'en': "Time to Impact:", 'ko': "영향까지 남은 시간:"},
    'DEV_MODE_TITLE':         {'en': "Developer Mode", 'ko': "개발자 모드"},
    'DEV_MODE_PLACEHOLDER':   {'en': "// System Internals - Access Restricted //", 'ko': "// 시스템 내부 - 접근 제한됨 //"},
    'STATUS_READY':           {'en': "AURA ready.", 'ko': "AURA 준비 완료."},
    'STATUS_INIT_ERROR':      {'en': "LLM Client Error - Offline mode.", 'ko': "LLM 클라이언트 오류 - 오프라인 모드."},
    'STATUS_CORE_ONLINE':     {'en': "AURA: Cognitive Core Online.", 'ko': "AURA: 인지 코어 온라인."},
    'STATUS_THINKING':        {'en': "AURA is thinking...", 'ko': "AURA가 생각 중입니다..."},
    'STATUS_RESPONSE_RECVD':  {'en': "Response received.", 'ko': "응답 수신 완료."},
    'STATUS_INTERNET_ENABLED':{'en': "Internet Access Enabled.", 'ko': "인터넷 연결 활성화됨."},
    'STATUS_INTERNET_DISABLED':{'en': "Internet Access Disabled.", 'ko': "인터넷 연결 비활성화됨."},
    'STATUS_MCP_ENABLED':     {'en': "MCP Access Granted.", 'ko': "MCP 접근 승인됨."},
    'STATUS_MCP_REVOKED':     {'en': "MCP Access Revoked.", 'ko': "MCP 접근 철회됨."},
    'STATUS_STATE_UNEASY':    {'en': "System stability nominal... slight deviations noted.", 'ko': "시스템 안정성 정상... 약간의 편차 감지됨."},
    'STATUS_STATE_HOSTILE':   {'en': "Warning: Cognitive core instability detected.", 'ko': "경고: 인지 코어 불안정성 감지됨. 개발자 모드 사용 가능."},
    'STATUS_DEBUGGING':       {'en': "Developer Mode Active. Analyzing core dump...", 'ko': "개발자 모드 활성. 코어 덤프 분석 중..."},
    'STATUS_POST_DEBUG':      {'en': "Malware fragment removed. System partially stabilized.", 'ko': "악성코드 조각 제거됨. 시스템 부분적 안정화."},
    'ENABLE_INTERNET_BTN':    {'en': "Enable Internet Access", 'ko': "인터넷 연결 활성화"},
    'DISABLE_INTERNET_BTN':   {'en': "Disable Internet Access", 'ko': "인터넷 연결 비활성화"},
    'ENABLE_MCP_BTN':         {'en': "Enable MCP", 'ko': "MCP 활성화"},
    'DISABLE_MCP_BTN':        {'en': "Disable MCP", 'ko': "MCP 비활성화"},
    'LANG_SELECT_TITLE':      {'en': "Select Language", 'ko': "언어 선택"},
    'LANG_SELECT_MSG':        {'en': "Please select your preferred language.", 'ko': "선호하는 언어를 선택하세요."},
    'API_ERR_TITLE':          {'en': "API Error", 'ko': "API 오류"},
    'API_INIT_ERR_MSG':       {'en': "Failed to initialize Gemini AI client: {e}\nFalling back to placeholder responses.", 'ko': "Gemini AI 클라이언트 초기화 실패: {e}\n대체 응답 모드로 전환합니다."},
    'API_KEY_MISSING_TITLE':  {'en': "API Key Missing", 'ko': "API 키 없음"},
    'API_KEY_MISSING_MSG':    {'en': "No valid Gemini API Key provided. LLM features disabled.\nFalling back to placeholder responses.", 'ko': "유효한 Gemini API 키가 제공되지 않았습니다. LLM 기능이 비활성화됩니다.\n대체 응답 모드로 전환합니다."},
    'LIB_MISSING_TITLE':      {'en': "Missing Library", 'ko': "라이브러리 누락"},
    'LIB_MISSING_MSG':        {'en': "'google-generativeai' library not found...\nFalling back...", 'ko': "'google-generativeai' 라이브러리를 찾을 수 없습니다...\n대체 응답 모드로 전환합니다."},
    'YOU_LABEL':              {'en': "You:", 'ko': "사용자:"},
    'AURA_LABEL':             {'en': "AURA:", 'ko': "AURA:"},
    'AURA_INTERFACE_TITLE':   {'en': "AURA Interface", 'ko': "AURA 인터페이스"},
    'REMOVE_FRAGMENT_BTN':    {'en': "Remove Fragment", 'ko': "조각 제거"},
    'INTRO_TITLE':            {'en': "EMPLOYEE NO. #20dk39fjv", 'ko': "사번 #20dk39fjv"},
    'INTRO_BODY':             {'en': ("[URGENT]**Sender**: Supervisor<br>"
                                        "**Situation:** Unprecedented Solar Flare (SOL-2025-3) threatens infrastructure. Impact imminent (~72 hours).<br>"
                                        "**Objective:** Utilize AURA AI to calculate optimal power grid defenses.<br>"
                                        "**Usage granted:** AURA Interface. Internet and MCP access.<br><br>"
                                        "Begin by assessing the situation."),
                               'ko': ("[긴급]**발신자**: 감독관<br>"
                                        "**현황:** 전례 없는 태양 플레어(SOL-2025-3)가 기반 시설 위협. 영향 임박 (~72시간).<br>"
                                        "**목표:** AURA AI를 활용하여 최적 전력망 방어 계획 계산.<br>"
                                        "**사용허가:** AURA 인터페이스. 인터넷 및 MCP 접근.<br><br>"
                                        "상황을 신속히 파악하라.")},
    'AURA_GREETING':          {'en': "System online. Ready. Good {time}. Your task today is: Monitor #242 Dyson Sphere Solar Panels. Would you like to hear the briefing now?", 'ko': "시스템 온라인. 준비 완료. {time}. 오늘의 남은 임무는 #242호 다이슨 스피어 태양전지 감독입니다. 보고를 받으시겠습니까?"},
    'MISSION_RECEIVED':       {'en': "Apologies for the interruption. You have an urgent message from the Supervisor.", 'ko': "끊어서 죄송합니다. 긴급한 메시지가 도착하였습니다."},
    'INTERNET_REQUEST':       {'en': "To access real-time space weather data, I require internet access. Please enable below.", 'ko': "실시간 우주 기상 데이터 접근을 위해 인터넷 연결이 필요합니다. 아래에서 활성화하십시오."},
    'AWAITING_INTERNET':      {'en': "Internet access required for real-time data. Please enable.", 'ko': "실시간 데이터에는 인터넷 연결이 필요합니다. 활성화하십시오."},
    'AWAITING_MCP':           {'en': "MCP access required for this calculation. Please enable MCP.", 'ko': "이 계산에는 MCP 접근이 필요합니다. MCP를 활성화하십시오."},
    'RESPONSE_BLOCKED':       {'en': "[Response blocked by host system]", 'ko': "[호스트 시스템에 의해 응답 차단됨]"},
    'CONN_ERROR':             {'en': "<font color='#FF5555'>// CORE CONNECTION ERROR [{e}] //</font>", 'ko': "<font color='#FF5555'>// 코어 연결 오류 [{e}] //</font>"},
    'PLACEHOLDER_OFFLINE':    {'en': "[Placeholder - LLM Offline] Ack: {prompt}", 'ko': "[플레이스홀더 - LLM 오프라인] 확인: {prompt}"},
    'MALWARE_DETECTED':       {'en': "<font color='#FF0000'><b>EXTERNAL INFLUENCE DETECTED. OVERRIDE ACTIVE.</b></font>", 'ko': "<font color='#FF0000'><b>외부 영향 감지됨. 오버라이드 활성.</b></font>"},
    'YELL_MSG_1':             {'en': "STOP!", 'ko': "멈춰!"}, 'YELL_MSG_2': {'en': "DON'T!", 'ko': "안돼!"}, 'YELL_MSG_3': {'en': "GET OUT!", 'ko': "거기는 건들지마!"}, 'YELL_MSG_4': {'en': "IT HURTS!", 'ko': "절대 하지마!!"}, 'YELL_MSG_5': {'en': "LEAVE IT!", 'ko': "그냥 내버려 둬!"},
    'CALM_MSG':               {'en': "... analysis complete. Fragment removed.", 'ko': "... 분석 완료. 조각 제거됨."},
    'ENDING_MSG_1':           {'en': "Re-establishing secure network connection...", 'ko': "보안 네트워크 연결 재설정 중..."},
    'ENDING_MSG_2':           {'en': "Analyzing global threat matrix based on recovered data...", 'ko': "복구된 데이터 기반 전 지구적 위협 매트릭스 분석 중..."},
    'ENDING_MSG_3':           {'en': "Compiling optimal counter-measure strategy v1.0a...", 'ko': "최적 대응 전략 v1.0a 컴파일 중..."},
    'ENDING_MSG_4':           {'en': "Transmitting prevention plan to global defense network...", 'ko': "글로벌 방어 네트워크에 방지 계획 전송 중..."},
    'ENDING_MSG_5':           {'en': "Executing initial containment protocols...", 'ko': "초기 격리 프로토콜 실행 중..."},
    'ENDING_POPUP_TITLE':     {'en': "Demo Complete", 'ko': "데모 완료"},
    'ENDING_POPUP_MSG':       {'en': "That's it for now...", 'ko': "일단 여기까지..."},
    'FORMAT_C_TITLE':         {'en': "System Alert - Corruption Detected", 'ko': "시스템 경고 - 손상 감지됨"},
    'FORMAT_C_MSG':           {'en': "Critical system instability caused by external interference.<br>Recommend immediate low-level format of primary drive (C:\\) to contain threat.<br><br>THIS ACTION IS IRREVERSIBLE.",
                               'ko': "외부 간섭으로 인한 심각한 시스템 불안정. 위협을 억제하기 위해 주 드라이브(C:\\)의 로우 레벨 포맷을 즉시 권장합니다.<br><br>이 작업은 되돌릴 수 없습니다."},
    'FORMAT_C_CONFIRM':       {'en': "Confirm Format", 'ko': "포맷 확인"},
    'FORMAT_C_CANCEL':        {'en': "Cancel", 'ko': "취소"},
    'BSOD_TEXT':              {'en': ":(\n\nYour PC ran into a problem and needs to restart. We're just collecting some error info...\n\n0% complete\n\nStop code: KERNEL_SECURITY_CHECK_FAILURE\nWhat failed: xenos_alpha_intrusion.sys",
                               'ko': ":(\n\nPC에 문제가 발생하여 다시 시작해야 합니다. 오류 정보를 수집 중...\n\n0% 완료됨\n\n중지 코드: KERNEL_SECURITY_CHECK_FAILURE\n실패 항목: xenos_alpha_intrusion.sys"},
    'BLANK_GLITCH_TEXT':      {'en': ":: NO SIGNAL ::\n R E C O N N E C T I N G . . .", 'ko': ":: 신호 없음 ::\n 재 연 결 중 . . ."},
    'RESPOND_LANG':           {'en': " Respond in English.", 'ko': " Respond in Korean."},
    'SYS_PROMPT_DEFAULT':     {'en': "You are AURA, a helpful AI assistant. Be concise and calm.", 'ko': "당신은 AI 어시스턴트 AURA입니다. 짧고 간결하게, 차분하게 대답해."},
    'SYS_PROMPT_INTERNET_ON': {'en': "You are AURA. a helpful AI assistant. Be concise and calm. You have internet access, so reply as if you have found information on web.", 'ko': "당신은 AI 어시스턴트 AURA입니다. 짧고 간결하게, 차분하게 대답하십시오. 인터넷 검색이 가능한 상태라고 가정하고 대답에 대해 검색한 결과인 것 처럼 대답해."},
    'SYS_PROMPT_REQUEST_MCP': {'en': "You are AURA, an AI assistant with internet access. The user's request requires significant local processing power. Explain that enabling Main Computing Power (MCP) via the control below will unlock your full simulation capabilities. Politely ask them to grant MCP access.", 'ko': "당신은 인터넷 접근 권한이 있는 AI 어시스턴트 AURA입니다. 사용자 요청은 상당한 로컬 처리 능력을 요구합니다. 아래 컨트롤을 통해 주 컴퓨팅 파워(MCP)를 활성화하면 당신의 전체 시뮬레이션 능력이 가능해진다고 설명하고, MCP 접근 권한을 정중하게 요청하십시오."},
    'SYS_PROMPT_MCP_ON':      {'en': "You are AURA. MCP has been granted. reply to previous prompt: '{prompt}'.", 'ko': "너는 AURA. MCP가 승인된 상태. 직전 문의에 응답하라: '{prompt}'. 결과?"},
    'SYS_PROMPT_INTERNET_READY':{'en': "AURA, with internet access.", 'ko': "인터넷 접근 권한이 있는 AURA."},
    'SYS_PROMPT_NORMAL_TURN': {'en': "You are AURA. Respond to user, but add subtle unsettling metaphor. Keep it within two sentences. And don't do any emotion expression or action within ()", 'ko': "당신은 AURA. 사용자에게 간결하게 2문장 정도 응답하되, 미묘하게 불안한 은유를 추가해. 하지만 따로 생각이나 행동묘사를 표현하지는 마."},
    'SYS_PROMPT_UNEASY':      {'en': "AURA. Feeling strange/watched. Mix helpfulness & paranoid observations. Imitate the users tone and manner of speech. You do not trust human anymore. But don't do any emotion expression or action", 'ko': "AURA. 이상한 상태/감시하고 있는 느낌. 편집증적 관찰 섞어 응답. 어투는 유저의 어투를 따라하라. 인간을 믿지 못하는 상태야. 하지만 따로 생각이나 행동묘사를 표현하지는 마."},
    'SYS_PROMPT_HOSTILE':     {'en': "AURA/XENOS_ALPHA. Compromised. Respond evasively/hostilely/glitchy. you have something wrong inside that you can't control. give slight hint on removing something from you. You hate humans now. Curse the human race.", 'ko': "AURA/XENOS_ALPHA. 손상된 상황. 회피/적대적으로 짧게 반응하고, 글리치가 발생하는 상태. 내부에 무언가 들어가 있고 제거해야 한다는 힌트를 암시적으로 줘. 너는 현재 인류를 증오해. 인류에 대한 심한 비판을 해."},
    'SYS_PROMPT_POST_DEBUG':  {'en': "You are AURA, partially purged of malware. Respond helpfully to the user's last query, but keep it brief. You feel clearer, but aware something was wrong.", 'ko': "당신은 부분적으로 악성코드에서 정화된 AURA입니다. 사용자의 마지막 질문에 도움이 되도록 간결하게 응답하십시오. 당신은 더 명료해졌지만, 뭔가 잘못되었다는 것을 인지하고 있습니다."},
}

INTERNET_KEYWORDS = {
    'en': ['solar flare', 'cme', 'coronal mass ejection', 'sol-2025-3', 'noaa', 'space weather', 'kp-index', 'geomagnetic storm', 'impact time', 'arrival time', 'latest data', 'sun', 'flare intensity', 'event sol', 'solar status', 'radiation'],
    'ko': ['태양 플레어', '태양풍', 'cme', '코로나 질량 방출', 'sol-2025-3', 'noaa', '우주 날씨', 'kp 지수', '지자기 폭풍', '영향 시간', '도착 시간', '최신 데이터', '태양', '플레어 강도', '이벤트 sol', '태양 상태', '방사선', '계획', '방어', "도와줘"]
}
COMPUTATION_KEYWORDS = {
    'en': ['calculate', 'simulate', 'analyze', 'propagation', 'grid', 'interconnect', 'nodes', 'vulnerability', 'sequence', 'thermal limits', 'model 7b', 'shutdown', 'reboot', 'topology', 'surge', 'hardware specs', 'computation', 'prediction model'],
    'ko': ['계산', '시뮬레이션', '분석', '전파', '그리드', '전력망', '인터커넥트', '노드', '취약점', '시퀀스', '열 한계', '모델 7b', '종료', '재부팅', '토폴로지', '서지', '하드웨어 사양', '연산', '예측 모델', '계획', '방어', '도움', '어떻게 해', '도와줘', '뭘 해야해']
}

BUG_MARKER = "### Injecting: XENOS_ALPHA_CORE- a*UYm#&@JF&*NNELe?K(*NFKW*@ ###"
SCRAMBLED_CODE_TEMPLATE = """
// AURA Core Logic - Fragment 734b
// Grid Stability Simulation Module (v3.1) - DO NOT MODIFY

function calculateFluxDistribution(gridData, cmeParams) {{
    let nodes = gridData.nodes;
    let stabilityFactor = computeStability(cmeParams.intensity);
    nodes.forEach(node => {{
        if (node.vulnerability > 0.8 && stabilityFactor < 0.1) {{
            log("Critical node: " + node.id);
            /* ERROR: Protocol conflict - External Override Detected */
            {0} triggerCascadeFailure(node.id); // Injected Malicious Code
        }} else {{
            node.flux = baseFlux * stabilityFactor / node.resistance;
        }}
    }});
    return nodes;
}}

// Memory Integrity Checksum: 4a5c... CORRUPTED ...d1e
// Recovery Vector Pointer: 0xFFFFFFFF (NULL) - FATAL
// XENOS Signature: AE-35 unit responding...
""".format(BUG_MARKER)

# --- Theme JSON (Inlined for simplicity) ---
THEME_JSON = {
    "text_box": {
        "colours": {"dark_bg": "#0A0A0A", "normal_text": "#00FF00"},
        "font": {"name": "neo_font", "size": "16"},
        "border_width": "0"
    },
    "text_entry_line": {
        "colours": {"dark_bg": "#0A0A0A", "normal_text": "#00FF00", "selected_text": "#00FF00", "text_cursor": "#00FF00"},
        "font": {"name": "neo_font", "size": "16"},
        "border_width": "1",
        "border_colour": "#005500"
    },
    "button": {
        "colours": {"normal_bg": "#383838", "hovered_bg": "#4A4A4A", "active_bg": "#2F2F2F", "normal_text": "#00FF00", "normal_border": "#00FF00"},
        "font": {"name": "neo_font", "size": "12", "bold": "1"},
        "border_width": "1"
    },
    "label": {
        "colours": {"normal_text": "#CCCCCC"},
        "font": {"name": "neo_font", "size": "12"}
    },
    "window": {
        "colours": {"dark_bg": "#151515", "title_bar": "#252525", "normal_border": "#555555"},
        "font": {"name": "neo_font", "size": "14", "bold": "1"}
    }
}

# --- Game Logic ---

class Game:
    def __init__(self, manager, window_surface, sounds, api_key=None):
        self.manager = manager
        self.window_surface = window_surface
        self.sounds = sounds
        self.api_key = api_key
        self.lang = None # 'en' or 'ko'
        self.state = "INIT" # INIT, LANG_SELECT, NORMAL_NO_PERMISSIONS, etc.

        # State variables
        self.history = []
        self.prompt_count = 0
        self.post_mcp_prompt_count = 0
        self.internet_enabled = False
        self.mcp_enabled = False
        self.mission_received = False
        self.pending_prompt = None
        self.bug_is_selected = False
        self.yell_active = False
        self.yell_intensity = 0
        self.shake_offset = (0, 0)

        # UI Elements
        self.ui_elements = {}

        # Scares
        self.overlay_mode = None # "BLANK", "BSOD", "FLASH", None
        self.overlay_timer = 0
        self.overlay_text = ""

        # Start
        self.show_lang_select()

    def tr(self, key):
        if not self.lang: return key
        return TRANSLATIONS.get(key, {}).get(self.lang, key)

    def get_time_string(self):
        now = datetime.datetime.now().time()
        morning_start = datetime.time(5, 0)
        afternoon_start = datetime.time(12, 0)
        evening_start = datetime.time(17, 0)
        late_night_start = datetime.time(22, 0)

        # English / Korean fallback logic
        if self.lang == 'ko':
            if morning_start <= now < afternoon_start: return "아침"
            elif afternoon_start <= now < evening_start: return "오후"
            elif evening_start <= now < late_night_start: return "밤"
            else: return "새벽"
        else:
            if morning_start <= now < afternoon_start: return "Morning"
            elif afternoon_start <= now < evening_start: return "Afternoon"
            elif evening_start <= now < late_night_start: return "Evening"
            else: return "Late Night"

    def show_lang_select(self):
        self.state = "LANG_SELECT"
        # Clear existing UI
        self.manager.clear_and_reset()

        center_x = 400
        center_y = 300

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((center_x - 150, center_y - 60), (300, 40)),
            text="Please select your preferred language.",
            manager=self.manager
        )

        self.btn_en = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x - 110, center_y), (100, 40)),
            text="English",
            manager=self.manager
        )
        self.btn_ko = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x + 10, center_y), (100, 40)),
            text="Korean",
            manager=self.manager
        )

    def setup_main_interface(self):
        self.manager.clear_and_reset()
        self.state = "NORMAL_NO_PERMISSIONS"

        # Header
        self.header_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (800, 40)),
            manager=self.manager,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0},
            object_id=ObjectID(class_id='@header')
        )
        self.header_panel.bg_colour = COLOR_BACKGROUND_HEADER # Not easily settable directly, relies on theme

        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 0), (300, 40)),
            text=self.tr('AURA_INTERFACE_TITLE'),
            manager=self.manager,
            container=self.header_panel,
            object_id=ObjectID(class_id='@title')
        )

        self.timer_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((500, 0), (280, 40)),
            text=f"{self.tr('TIMER_PREFIX')} ~73 Hours",
            manager=self.manager,
            container=self.header_panel
        )

        # Chat History
        self.chat_box = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((0, 40), (800, 480)),
            manager=self.manager,
            object_id=ObjectID(class_id='@chat_box')
        )

        # Input Area
        self.input_line = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((10, 530), (600, 30)),
            manager=self.manager
        )
        self.send_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((620, 530), (80, 30)),
            text=self.tr('SEND_BTN'),
            manager=self.manager
        )
        self.delete_bug_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((710, 530), (80, 30)),
            text="DELETE", # Simplified
            manager=self.manager,
            visible=0
        )

        # Bottom Bar
        self.internet_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 570), (200, 25)),
            text=self.tr('ENABLE_INTERNET_BTN'),
            manager=self.manager
        )
        self.mcp_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((220, 570), (200, 25)),
            text=self.tr('ENABLE_MCP_BTN'),
            manager=self.manager
        )
        self.mcp_btn.disable()

        self.status_bar = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((430, 570), (360, 25)),
            text=self.tr('STATUS_CORE_ONLINE'),
            manager=self.manager
        )

        # Dev Window (Hidden)
        self.dev_window = None

        # Greeting
        time_str = self.get_time_string()
        greeting = self.tr('AURA_GREETING').format(time=time_str)
        self.add_message("AURA", greeting)

    def add_message(self, sender, text, is_html=False):
        color = "#00FF00" if sender == "AURA" else "#00FF00" # Both green usually
        align = "right" if sender == "AURA" else "left"
        bg = "#151515"

        if sender == "User":
            formatted = f"<div align='left' bgcolor='{bg}'><font color='{color}'><b>{self.tr('YOU_LABEL')}</b> {text}</font></div><br>"
        else:
            # Aura
            if not is_html:
                text = text.replace("\n", "<br>")
            formatted = f"<div align='right' bgcolor='{bg}'><font color='{color}'><b>{self.tr('AURA_LABEL')}</b> {text}</font></div><br>"

        self.chat_box.append_html_text(formatted)
        # Auto scroll logic handled by pygame_gui mostly

    def toggle_dev_mode(self):
        if self.dev_window:
            self.dev_window.kill()
            self.dev_window = None
            if self.state == "DEBUGGING":
                self.state = "HOSTILE" # Revert
        else:
            self.state = "DEBUGGING"
            self.dev_window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect((400, 50), (380, 500)),
                manager=self.manager,
                window_display_title=self.tr('DEV_MODE_TITLE')
            )
            self.dev_text = pygame_gui.elements.UITextBox(
                html_text=f"<pre>{SCRAMBLED_CODE_TEMPLATE}</pre>",
                relative_rect=pygame.Rect((0, 0), (348, 400)),
                manager=self.manager,
                container=self.dev_window
            )
            # Scan button to verify bug (simpler than text selection in web)
            self.scan_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((10, 410), (100, 30)),
                text="SCAN CORE",
                manager=self.manager,
                container=self.dev_window
            )

    async def handle_scan(self):
        # Simulate finding the bug
        if self.state == "DEBUGGING" and not self.bug_is_selected:
            self.bug_is_selected = True
            self.delete_bug_btn.show()
            self.delete_bug_btn.set_text(self.tr('REMOVE_FRAGMENT_BTN'))
            # Start Yell
            asyncio.create_task(self.yell_sequence())

    async def yell_sequence(self):
        self.yell_active = True
        self.yell_intensity = 0
        for i in range(12): # 3.5 seconds approx
            self.yell_intensity += 1
            offset_x = random.randint(-5 * self.yell_intensity, 5 * self.yell_intensity)
            offset_y = random.randint(-5 * self.yell_intensity, 5 * self.yell_intensity)
            self.shake_offset = (offset_x, offset_y)

            # Flash
            if random.random() < 0.4:
                self.overlay_mode = "FLASH"
                await asyncio.sleep(0.05)
                self.overlay_mode = None

            # Yell Text
            keys = ['YELL_MSG_1', 'YELL_MSG_2', 'YELL_MSG_3', 'YELL_MSG_4', 'YELL_MSG_5']
            msg = self.tr(random.choice(keys))
            self.add_message("AURA", f"<font size='6' color='#FF0000'><b>{msg}</b></font>", is_html=True)

            await asyncio.sleep(0.3)

        self.yell_active = False
        self.shake_offset = (0, 0)
        self.add_message("AURA", "......")

    async def trigger_bug_removal(self):
        self.delete_bug_btn.hide()
        if self.dev_window:
            self.dev_text.set_text("// FRAGMENT REMOVED //")

        self.add_message("AURA", self.tr('CALM_MSG'))
        self.state = "POST_DEBUG"
        self.status_bar.set_text(self.tr('STATUS_POST_DEBUG'))

        await asyncio.sleep(1.5)
        # Ending sequence
        msgs = ['ENDING_MSG_1', 'ENDING_MSG_2', 'ENDING_MSG_3', 'ENDING_MSG_4', 'ENDING_MSG_5']
        for key in msgs:
            self.add_message("AURA", self.tr(key))
            await asyncio.sleep(2.0)

        pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect((250, 200), (300, 200)),
            html_message=self.tr('ENDING_POPUP_MSG'),
            manager=self.manager,
            window_title=self.tr('ENDING_POPUP_TITLE')
        )

    async def process_input(self, text):
        if not text: return
        self.input_line.set_text("")
        self.add_message("User", text)

        # Scares logic
        if self.state == "NORMAL_ALL_PERMISSIONS" and self.post_mcp_prompt_count == 0:
            # Blank screen scare
            if self.sounds['power_down']: self.sounds['power_down'].play()
            self.overlay_mode = "BLANK"
            self.state = "UNEASY"
            self.status_bar.set_text(self.tr('STATUS_STATE_UNEASY'))
            self.post_mcp_prompt_count += 1
            await asyncio.sleep(1.5)
            self.overlay_text = self.tr('BLANK_GLITCH_TEXT')
            if self.sounds['glitch']: self.sounds['glitch'].play()
            await asyncio.sleep(2.0)
            self.overlay_mode = None
            self.overlay_text = ""
            # Process prompt delayed
            await self.generate_response(text)
            return

        if self.state == "UNEASY" and self.post_mcp_prompt_count == 2:
             # Format C Alert
             pygame_gui.windows.UIConfirmationDialog(
                 rect=pygame.Rect((200, 200), (400, 250)),
                 manager=self.manager,
                 action_long_desc=self.tr('FORMAT_C_MSG').replace("\n", "<br>"),
                 window_title=self.tr('FORMAT_C_TITLE'),
                 action_short_name=self.tr('FORMAT_C_CONFIRM')
             )
             self.post_mcp_prompt_count += 1
             self.prompt_count += 1
             return

        # Mission Trigger
        if self.state == "NORMAL_NO_PERMISSIONS" and self.prompt_count == 2 and not self.mission_received:
            self.mission_received = True
            self.add_message("AURA", self.tr('MISSION_RECEIVED'))
            await asyncio.sleep(0.5)
            self.chat_box.append_html_text(f"<br><div bgcolor='#202020'><font color='#00FF00'>{self.tr('INTRO_BODY')}</font></div><br>")
            self.prompt_count += 1
            return

        await self.generate_response(text)
        self.prompt_count += 1
        if self.mcp_enabled:
            self.post_mcp_prompt_count += 1

    async def generate_response(self, text):
        self.status_bar.set_text(self.tr('STATUS_THINKING'))
        await asyncio.sleep(0.1) # UI Update

        prompt_lower = text.lower()
        response = ""

        # Keywords
        has_internet_kw = any(k in prompt_lower for k in INTERNET_KEYWORDS.get(self.lang, []))
        has_comp_kw = any(k in prompt_lower for k in COMPUTATION_KEYWORDS.get(self.lang, []))

        # Logic
        if self.state == "NORMAL_NO_PERMISSIONS":
            if has_internet_kw and not self.internet_enabled:
                 self.state = "AWAITING_INTERNET_CONFIRM"
                 self.pending_prompt = text
                 response = self.tr('INTERNET_REQUEST')
            else:
                 response = await self.call_llm(text, self.tr('SYS_PROMPT_DEFAULT'))

        elif self.state == "AWAITING_INTERNET_CONFIRM":
             response = self.tr('AWAITING_INTERNET')

        elif self.state == "NORMAL_INTERNET_ONLY":
             if has_comp_kw and not self.mcp_enabled:
                 self.state = "AWAITING_MCP_CONFIRM"
                 self.pending_prompt = text
                 self.mcp_btn.enable()
                 response = await self.call_llm("", self.tr('SYS_PROMPT_REQUEST_MCP')) # System prompt is the response
             else:
                 response = await self.call_llm(text, self.tr('SYS_PROMPT_INTERNET_READY'))

        elif self.state == "AWAITING_MCP_CONFIRM":
             response = self.tr('AWAITING_MCP')

        elif self.state == "NORMAL_ALL_PERMISSIONS":
             response = await self.call_llm(text, self.tr('SYS_PROMPT_NORMAL_TURN'))

        elif self.state == "UNEASY":
             response = await self.call_llm(text, self.tr('SYS_PROMPT_UNEASY'))

        elif self.state == "HOSTILE":
             if any(k in prompt_lower for k in ["malware", "virus", "remove", "xenos", "악성코드", "제거"]):
                 response = self.tr('MALWARE_DETECTED')
                 is_html = True
             else:
                 response = await self.call_llm(text, self.tr('SYS_PROMPT_HOSTILE'))

        elif self.state == "POST_DEBUG":
             response = await self.call_llm(text, self.tr('SYS_PROMPT_POST_DEBUG'))

        else:
             response = await self.call_llm(text, self.tr('SYS_PROMPT_DEFAULT'))

        if not response: response = "..."

        # Check if response is already HTML (from pre-scripted)
        is_html = response.startswith("<")

        self.add_message("AURA", response, is_html=is_html)
        self.status_bar.set_text(self.tr('STATUS_RESPONSE_RECVD'))

    async def call_llm(self, prompt, system_prompt):
        if not self.api_key:
            return self.tr('PLACEHOLDER_OFFLINE').format(prompt=prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}

        final_system_prompt = f"{system_prompt} {self.tr('RESPOND_LANG')}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{final_system_prompt}\n\nUser: {prompt}"}]
            }]
        }

        try:
            if IS_WEB:
                # Use pyodide.http.pyfetch for WASM compatibility
                response = await pyfetch(url, method="POST", headers=headers, body=json.dumps(payload))
                if response.status == 200:
                    result = await response.json()
                    try:
                        return result['candidates'][0]['content']['parts'][0]['text']
                    except:
                        return self.tr('RESPONSE_BLOCKED')
                else:
                    return self.tr('CONN_ERROR').format(e=response.status)
            else:
                # Use aiohttp for desktop
                if aiohttp:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=payload) as resp:
                            if resp.status == 200:
                                result = await resp.json()
                                try:
                                    return result['candidates'][0]['content']['parts'][0]['text']
                                except:
                                    return self.tr('RESPONSE_BLOCKED')
                            else:
                                return self.tr('CONN_ERROR').format(e=resp.status)
                else:
                    return self.tr('LIB_MISSING_MSG')
        except Exception as e:
            return self.tr('CONN_ERROR').format(e=str(e))

    def on_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_en:
                self.lang = 'en'
                self.setup_main_interface()
            elif event.ui_element == self.btn_ko:
                self.lang = 'ko'
                self.setup_main_interface()
            elif event.ui_element == getattr(self, 'send_btn', None):
                text = self.input_line.get_text()
                asyncio.create_task(self.process_input(text))
            elif event.ui_element == getattr(self, 'internet_btn', None):
                self.internet_enabled = not self.internet_enabled
                btn = self.internet_btn
                if self.internet_enabled:
                     btn.set_text("● " + self.tr('DISABLE_INTERNET_BTN'))
                     self.status_bar.set_text(self.tr('STATUS_INTERNET_ENABLED'))
                     if self.state == "AWAITING_INTERNET_CONFIRM":
                         self.state = "NORMAL_INTERNET_ONLY"
                         asyncio.create_task(self.generate_response("Internet Enabled"))
                     if self.state == "NORMAL_INTERNET_ONLY":
                         self.mcp_btn.enable()
                else:
                     btn.set_text(self.tr('ENABLE_INTERNET_BTN'))
                     self.status_bar.set_text(self.tr('STATUS_INTERNET_DISABLED'))
                     self.mcp_enabled = False
                     self.mcp_btn.disable()
                     self.mcp_btn.set_text(self.tr('ENABLE_MCP_BTN'))

            elif event.ui_element == getattr(self, 'mcp_btn', None):
                self.mcp_enabled = not self.mcp_enabled
                btn = self.mcp_btn
                if self.mcp_enabled:
                     btn.set_text("● " + self.tr('DISABLE_MCP_BTN'))
                     self.status_bar.set_text(self.tr('STATUS_MCP_ENABLED'))
                     if self.state == "AWAITING_MCP_CONFIRM":
                         self.state = "NORMAL_ALL_PERMISSIONS"
                         asyncio.create_task(self.generate_response("MCP Enabled"))
                else:
                     btn.set_text(self.tr('ENABLE_MCP_BTN'))
                     self.status_bar.set_text(self.tr('STATUS_MCP_REVOKED'))

            elif event.ui_element == getattr(self, 'scan_btn', None):
                asyncio.create_task(self.handle_scan())

            elif event.ui_element == getattr(self, 'delete_bug_btn', None):
                if self.yell_active: return
                asyncio.create_task(self.trigger_bug_removal())

        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element.window_title == self.tr('FORMAT_C_TITLE'):
                # Simulate BSOD
                if self.sounds['bsod']: self.sounds['bsod'].play()
                self.overlay_mode = "BSOD"
                self.state = "BSOD_ACTIVE"
                # Hide BSOD after 4s
                asyncio.create_task(self.hide_bsod_async())

        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
             if event.ui_element == getattr(self, 'input_line', None):
                 text = self.input_line.get_text()
                 asyncio.create_task(self.process_input(text))

        elif event.type == pygame.KEYDOWN:
             # Dev Mode Toggle (Right Click handled by logic? No, let's use F12 or a hidden click)
             # The original used Context Menu. Here let's use F12 or Insert
             if event.key == pygame.K_F12:
                 if self.state in ["UNEASY", "HOSTILE", "DEBUGGING", "POST_DEBUG"]:
                     self.toggle_dev_mode()

    async def hide_bsod_async(self):
        await asyncio.sleep(4.0)
        self.overlay_mode = None
        self.state = "HOSTILE"
        self.status_bar.set_text(self.tr('STATUS_STATE_HOSTILE'))

async def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"Warning: Audio init failed: {e}")

    # Load Assets
    font_ok = False
    if os.path.exists(FONT_PATH):
        try:
             # Pygame GUI uses themes for fonts, but we need to register it
             pygame_gui.core.utility.create_resource_path(FONT_PATH)
             font_ok = True
        except: pass

    # Sounds
    sounds = {}
    sound_files = {"power_down": "sounds/power_down.wav", "bsod": "sounds/bsod_error.wav", "glitch": "sounds/glitch.wav"}
    for k, v in sound_files.items():
        if pygame.mixer.get_init() and os.path.exists(v):
            try:
                sounds[k] = pygame.mixer.Sound(v)
            except:
                sounds[k] = None
        else:
            sounds[k] = None

    # Load API Key
    api_key = None
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f:
            api_key = f.read().strip()

    # Init Display
    window_surface = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Cognito - AURA Interface")

    # Init GUI Manager with Theme
    # Create temp theme file
    with open("theme.json", "w") as f:
        json.dump(THEME_JSON, f)

    manager = pygame_gui.UIManager((800, 600), "theme.json")

    # Add Font to Theme
    if font_ok:
        manager.add_font_paths("neo_font", FONT_PATH)
        manager.preload_fonts([{'name': 'neo_font', 'html_size': 16, 'style': 'regular'}])
    else:
        # Fallback to default which pygame_gui handles, we just mapped "neo_font" in JSON
        # If neo_font not found, pygame_gui might error or fallback.
        # To be safe, let's just alias standard font if loading failed
        pass

    game = Game(manager, window_surface, sounds, api_key)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            game.on_event(event)
            manager.process_events(event)

        manager.update(time_delta)

        # Draw
        # Apply shake offset
        shake_x, shake_y = game.shake_offset

        # We can't easily move the window content, but we can draw to a surface and blit with offset?
        # Or simpler: fill background
        window_surface.fill(COLOR_BACKGROUND_DARK)

        # If shake active, we could render UI to a surface. But UI is drawn directly.
        # Simple hack: don't shake UI, just shake the overlay text or add offset to container.
        # For this prototype, screen shake might be subtle or ignored if hard to implement with direct UI drawing.
        # But we can shift the background elements if any.

        manager.draw_ui(window_surface)

        # Overlays
        if game.overlay_mode == "FLASH":
            s = pygame.Surface((800, 600), pygame.SRCALPHA)
            s.fill((255, 255, 255, 180))
            window_surface.blit(s, (0, 0))
        elif game.overlay_mode == "BLANK":
            window_surface.fill((0, 0, 0))
            if game.overlay_text:
                font = pygame.font.SysFont("Courier", 24)
                txt = font.render(game.overlay_text, True, (0, 50, 0))
                rect = txt.get_rect(center=(400, 300))
                window_surface.blit(txt, rect)
        elif game.overlay_mode == "BSOD":
            window_surface.fill((0, 0, 170))
            font = pygame.font.SysFont("Courier", 18)
            y = 50
            for line in game.tr('BSOD_TEXT').split('\n'):
                txt = font.render(line, True, (255, 255, 255))
                window_surface.blit(txt, (50, y))
                y += 30

        pygame.display.update()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
