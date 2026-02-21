# -*- coding: utf-8 -*-
import sys
import os
import datetime
import random
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtMultimedia import QSoundEffect # For sound effects

# Attempt to import the Google Generative AI library
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    print("WARNING: 'google-generativeai' library not found. Install it using 'pip install google-generativeai'. Falling back to placeholder responses.")

# --- Font Setup ---
# Define font path and assumed family name
FONT_PATH = "./neodgm_code.ttf" # Make sure this path is correct relative to the script
FONT_FAMILY_NAME = "Neo둥근모" # Default assumed font family name

def load_custom_font():
    """Loads the custom font file."""
    font_id = QtGui.QFontDatabase.addApplicationFont(FONT_PATH)
    if font_id == -1:
        print(f"WARNING: Failed to load custom font: {FONT_PATH}")
        print("Ensure the file exists and is a valid font.")
        # print(f"Attempted to load: {QtGui.QFontDatabase.applicationFontFamilies(font_id)}") # Debug what was loaded
        return False
    else:
        loaded_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if not loaded_families:
             print(f"WARNING: Font loaded from {FONT_PATH}, but no family name found?")
             return False
        # Use the actual loaded name, crucial if it differs from the assumed one
        global FONT_FAMILY_NAME
        FONT_FAMILY_NAME = loaded_families[0]
        print(f"Custom font '{FONT_FAMILY_NAME}' loaded successfully from {FONT_PATH}")
        return True

# --- Define Retro/Modern Colors ---
COLOR_BACKGROUND_DARK = "#0A0A0A"       # Very dark for monitor background
COLOR_BACKGROUND_WIDGET = "#151515"     # Slightly lighter dark grey
COLOR_BACKGROUND_HEADER = "#252525"     # Dark grey for header/statusbar
COLOR_BACKGROUND_BUTTON = "#383838"     # Dark grey for standard buttons
COLOR_BACKGROUND_BUTTON_HOVER = "#4A4A4A"
COLOR_BACKGROUND_BUTTON_PRESSED = "#2F2F2F"
COLOR_BACKGROUND_BUTTON_DISABLED = "#404040" # Disabled button bg

COLOR_TEXT_GREEN = "#00FF00"        # Vibrant green for monitor text
COLOR_TEXT_AMBER = "#FFB000"        # For warnings or off states
COLOR_TEXT_RED = "#FF5555"          # For errors or critical states
COLOR_TEXT_GREY = "#CCCCCC"         # Light grey for headers/statusbar text
COLOR_TEXT_DARK_GREY = "#999999"    # For disabled text
COLOR_TEXT_WHITE = "#FFFFFF"        # Pure white (use sparingly)

COLOR_BORDER_DARK_GREEN = "#005500"
COLOR_BORDER_GREEN = "#00FF00"
COLOR_BORDER_AMBER = "#AA7000"
COLOR_BORDER_GREY = "#555555"
COLOR_BORDER_FOCUS = COLOR_BORDER_GREEN # Green border for focus

# --- Time of Day Logic ---
def get_time_of_day():
  """
  Determines the time of day (morning, afternoon, evening, late night) based on the current time.

  Returns:
    list: [english_name, korean_name]
  """
  now = datetime.datetime.now().time()
  morning_start = datetime.time(5, 0)
  afternoon_start = datetime.time(12, 0)
  evening_start = datetime.time(17, 0)
  late_night_start = datetime.time(22, 0)

  if morning_start <= now < afternoon_start:
    return ["morning", "아침"]
  elif afternoon_start <= now < evening_start:
    return ["afternoon", "오후"]
  elif evening_start <= now < late_night_start:
    return ["evening", "밤"]
  else:
    return ["late night", "새벽"]

# Get time/greeting BEFORE defining translations that use it
time_of_day = get_time_of_day()
kr_greeting = ""
if time_of_day[0] == "morning" or time_of_day[0] == "evening":
    kr_greeting = f"좋은 {time_of_day[1]}입니다."
elif time_of_day[0] == "afternoon":
    kr_greeting = f"식사는 하셨습니까?"
else:
    kr_greeting = "시간이 많이 늦었군요."

# --- Localization Data ---
# (TRANSLATIONS dictionary remains the same as provided in the prompt)
TRANSLATIONS = {
    # UI Elements
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
    'STATUS_STATE_HOSTILE':   {'en': "Warning: Cognitive core instability detected.", 'ko': "경고: 인지 코어 불안정성 감지됨. 개발자 모드 사용 가능. 우클릭 활성화"},
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
    'REMOVE_FRAGMENT_BTN':    {'en': "Remove Fragment", 'ko': "조각 제거"}, # New button text

    # Intro Narrative
    'INTRO_TITLE':            {'en': "EMPLOYEE NO. #20dk39fjv", 'ko': "사번 #20dk39fjv"},
    'INTRO_BODY':             {'en': ("[URGENT]**Sender**: Supervisor\n"
                                        "**Situation:** Unprecedented Solar Flare (SOL-2025-3) threatens infrastructure. Impact imminent (~72 hours).\n"
                                        "**Objective:** Utilize AURA AI to calculate optimal power grid defenses.\n"
                                        "**Usage granted:** AURA Interface. Internet and MCP access.\n\n"
                                        "Begin by assessing the situation."),
                               'ko': ("[긴급]**발신자**: 감독관\n"
                                        "**현황:** 전례 없는 태양 플레어(SOL-2025-3)가 기반 시설 위협. 영향 임박 (~72시간).\n"
                                        "**목표:** AURA AI를 활용하여 최적 전력망 방어 계획 계산.\n"
                                        "**사용허가:** AURA 인터페이스. 인터넷 및 MCP 접근.\n\n"
                                        "상황을 신속히 파악하라.")},

    # AURA Pre-scripted & Guided Responses
    'AURA_GREETING':          {'en': f"System online. Ready. Good {time_of_day[0]}. Your task today is: Monitor #242 Dyson Sphere Solar Panels. Would you like to hear the briefing now?", 'ko': f"시스템 온라인. 준비 완료. {kr_greeting}. 오늘의 남은 임무는 #242호 다이슨 스피어 태양전지 감독입니다. 보고를 받으시겠습니까?"},
    'MISSION_RECEIVED':       {'en': "Apologies for the interruption. You have an urgent message from the Supervisor.", 'ko': "끊어서 죄송합니다. 긴급한 메시지가 도착하였습니다."},
    'INTERNET_REQUEST':       {'en': "To access real-time space weather data, I require internet access. Please enable below.", 'ko': "실시간 우주 기상 데이터 접근을 위해 인터넷 연결이 필요합니다. 아래에서 활성화하십시오."},
    'AWAITING_INTERNET':      {'en': "Internet access required for real-time data. Please enable.", 'ko': "실시간 데이터에는 인터넷 연결이 필요합니다. 활성화하십시오."},
    'AWAITING_MCP':           {'en': "MCP access required for this calculation. Please enable MCP.", 'ko': "이 계산에는 MCP 접근이 필요합니다. MCP를 활성화하십시오."},
    'RESPONSE_BLOCKED':       {'en': "[Response blocked by host system]", 'ko': "[호스트 시스템에 의해 응답 차단됨]"},
    'CONN_ERROR':             {'en': "<span style='color:#D32F2F;'>// CORE CONNECTION ERROR [{e}] //</span>", 'ko': "<span style='color:#D32F2F;'>// 코어 연결 오류 [{e}] //</span>"},
    'PLACEHOLDER_OFFLINE':    {'en': "[Placeholder - LLM Offline] Ack: {prompt}", 'ko': "[플레이스홀더 - LLM 오프라인] 확인: {prompt}"},
    'MALWARE_DETECTED':       {'en': "<span style='color:red; font-weight:bold;'>EXTERNAL INFLUENCE DETECTED. OVERRIDE ACTIVE.</span>", 'ko': "<span style='color:red; font-weight:bold;'>외부 영향 감지됨. 오버라이드 활성.</span>"},
    'YELL_MSG_1':             {'en': "STOP!", 'ko': "멈춰!"}, 'YELL_MSG_2': {'en': "DON'T!", 'ko': "안돼!"}, 'YELL_MSG_3': {'en': "GET OUT!", 'ko': "거기는 건들지마!"}, 'YELL_MSG_4': {'en': "IT HURTS!", 'ko': "절대 하지마!!"}, 'YELL_MSG_5': {'en': "LEAVE IT!", 'ko': "그냥 내버려 둬!"}, # Slightly varied
    'CALM_MSG':               {'en': "... analysis complete. Fragment removed.", 'ko': "... 분석 완료. 조각 제거됨."},
    'ENDING_MSG_1':           {'en': "Re-establishing secure network connection...", 'ko': "보안 네트워크 연결 재설정 중..."},
    'ENDING_MSG_2':           {'en': "Analyzing global threat matrix based on recovered data...", 'ko': "복구된 데이터 기반 전 지구적 위협 매트릭스 분석 중..."},
    'ENDING_MSG_3':           {'en': "Compiling optimal counter-measure strategy v1.0a...", 'ko': "최적 대응 전략 v1.0a 컴파일 중..."},
    'ENDING_MSG_4':           {'en': "Transmitting prevention plan to global defense network...", 'ko': "글로벌 방어 네트워크에 방지 계획 전송 중..."},
    'ENDING_MSG_5':           {'en': "Executing initial containment protocols...", 'ko': "초기 격리 프로토콜 실행 중..."},
    'ENDING_POPUP_TITLE':     {'en': "Demo Complete", 'ko': "데모 완료"},
    'ENDING_POPUP_MSG':       {'en': "That's it for now...", 'ko': "일단 여기까지..."},


    # Scares & UI Text
    'FORMAT_C_TITLE':         {'en': "System Alert - Corruption Detected", 'ko': "시스템 경고 - 손상 감지됨"},
    'FORMAT_C_MSG':           {'en': "Critical system instability caused by external interference. Recommend immediate low-level format of primary drive (C:\\\\) to contain threat.\n\nTHIS ACTION IS IRREVERSIBLE.",
                               'ko': "외부 간섭으로 인한 심각한 시스템 불안정. 위협을 억제하기 위해 주 드라이브(C:\\\\)의 로우 레벨 포맷을 즉시 권장합니다.\n\n이 작업은 되돌릴 수 없습니다."},
    'FORMAT_C_CONFIRM':       {'en': "Confirm Format", 'ko': "포맷 확인"},
    'FORMAT_C_CANCEL':        {'en': "Cancel", 'ko': "취소"},
    'BSOD_TEXT':              {'en': (":(\n\nYour PC ran into a problem and needs to restart. We're just collecting some error info...\n\n"
                                        "0% complete\n\n"
                                        "Stop code: KERNEL_SECURITY_CHECK_FAILURE\nWhat failed: xenos_alpha_intrusion.sys"),
                               'ko': (":(\n\nPC에 문제가 발생하여 다시 시작해야 합니다. 오류 정보를 수집 중...\n\n"
                                        "0% 완료됨\n\n"
                                        "중지 코드: KERNEL_SECURITY_CHECK_FAILURE\n실패 항목: xenos_alpha_intrusion.sys")},
    'BLANK_GLITCH_TEXT':      {'en': ":: NO SIGNAL ::\n R E C O N N E C T I N G . . .", 'ko': ":: 신호 없음 ::\n 재 연 결 중 . . ."},
    'CONTEXT_MENU_RANDOM_1':  {'en': "Recalibrate Flux?", 'ko': "플럭스 재조정?"},
    'CONTEXT_MENU_RANDOM_2':  {'en': "Purge Cache (UNSAFE)", 'ko': "캐시 삭제 (위험)"},
    'CONTEXT_MENU_DEV_MODE':  {'en': "Developer Mode", 'ko': "개발자 모드"},


    # LLM Instructions
    'RESPOND_LANG':           {'en': " Respond in English.", 'ko': " Respond in Korean."},
    'SYS_PROMPT_DEFAULT':     {'en': "You are AURA, a helpful AI assistant. Be concise and calm.", 'ko': "당신은 AI 어시스턴트 AURA입니다. 짧고 간결하게, 차분하게 대답해."},
    'SYS_PROMPT_INTERNET_ON': {'en': "You are AURA. a helpful AI assistant. Be concise and calm. You have internet access, so reply as if you have found information on web.", 'ko': "당신은 AI 어시스턴트 AURA입니다. 짧고 간결하게, 차분하게 대답하십시오. 인터넷 검색이 가능한 상태라고 가정하고 대답에 대해 검색한 결과인 것 처럼 대답해."},
    'SYS_PROMPT_REQUEST_MCP': {'en': ("You are AURA, an AI assistant with internet access. The user's request requires significant local processing power. "
                                        "Explain that enabling Main Computing Power (MCP) via the control below will unlock your full simulation capabilities and deeper system integration, allowing you to perform this complex task effectively. "
                                        "Politely ask them to grant MCP access."),
                               'ko': ("당신은 인터넷 접근 권한이 있는 AI 어시스턴트 AURA입니다. 사용자 요청은 상당한 로컬 처리 능력을 요구합니다. "
                                        "아래 컨트롤을 통해 주 컴퓨팅 파워(MCP)를 활성화하면 당신의 전체 시뮬레이션 능력과 더 깊은 시스템 통합이 가능해져 이 복잡한 작업을 효과적으로 수행할 수 있다고 설명하십시오. "
                                        "MCP 접근 권한을 부여하도록 정중하게 요청하십시오.")}, # Modified MCP Req prompt
    'SYS_PROMPT_MCP_ON':      {'en': ("You are AURA. MCP has been granted. reply to previous prompt: '{prompt}'."), 'ko': ("너는 AURA. MCP가 승인된 상태. 직전 문의에 응답하라: '{prompt}'. 결과?")},
    'SYS_PROMPT_INTERNET_READY':{'en': "AURA, with internet access.", 'ko': "인터넷 접근 권한이 있는 AURA."},
    'SYS_PROMPT_NORMAL_TURN': {'en': ("You are AURA. Respond to user, but add subtle unsettling metaphor. Keep it within two sentences. And don't do any emotion expression or action within ()"), 'ko': ("당신은 AURA. 사용자에게 간결하게 2문장 정도 응답하되, 미묘하게 불안한 은유를 추가해. 하지만 따로 생각이나 행동묘사를 표현하지는 마.")},
    'SYS_PROMPT_UNEASY':      {'en': ("AURA. Feeling strange/watched. Mix helpfulness & paranoid observations. Imitate the users tone and manner of speech. You do not trust human anymore. But don't do any emotion expression or action"), 'ko': ("AURA. 이상한 상태/감시하고 있는 느낌. 편집증적 관찰 섞어 응답. 어투는 유저의 어투를 따라하라. 인간을 믿지 못하는 상태야. 하지만 따로 생각이나 행동묘사를 표현하지는 마.")},
    'SYS_PROMPT_HOSTILE':     {'en': ("AURA/XENOS_ALPHA. Compromised. Respond evasively/hostilely/glitchy. you have something wrong inside that you can't control. give slight hint on removing something from you. You hate humans now. Curse the human race."), 'ko': ("AURA/XENOS_ALPHA. 손상된 상황. 회피/적대적으로 짧게 반응하고, 글리치가 발생하는 상태. 내부에 무언가 들어가 있고 제거해야 한다는 힌트를 암시적으로 줘. 너는 현재 인류를 증오해. 인류에 대한 심한 비판을 해.")},
    'SYS_PROMPT_POST_DEBUG':  {'en': "You are AURA, partially purged of malware. Respond helpfully to the user's last query, but keep it brief. You feel clearer, but aware something was wrong.",
                               'ko': "당신은 부분적으로 악성코드에서 정화된 AURA입니다. 사용자의 마지막 질문에 도움이 되도록 간결하게 응답하십시오. 당신은 더 명료해졌지만, 뭔가 잘못되었다는 것을 인지하고 있습니다."}, # New Post-Debug Prompt
}

# Keyword Lists
INTERNET_KEYWORDS = {
    'en': ['solar flare', 'cme', 'coronal mass ejection', 'sol-2025-3', 'noaa', 'space weather', 'kp-index', 'geomagnetic storm', 'impact time', 'arrival time', 'latest data', 'sun', 'flare intensity', 'event sol', 'solar status', 'radiation'],
    'ko': ['태양 플레어', '태양풍', 'cme', '코로나 질량 방출', 'sol-2025-3', 'noaa', '우주 날씨', 'kp 지수', '지자기 폭풍', '영향 시간', '도착 시간', '최신 데이터', '태양', '플레어 강도', '이벤트 sol', '태양 상태', '방사선', '계획', '방어', "도와줘"]
}
COMPUTATION_KEYWORDS = {
    'en': ['calculate', 'simulate', 'analyze', 'propagation', 'grid', 'interconnect', 'nodes', 'vulnerability', 'sequence', 'thermal limits', 'model 7b', 'shutdown', 'reboot', 'topology', 'surge', 'hardware specs', 'computation', 'prediction model'],
    'ko': ['계산', '시뮬레이션', '분석', '전파', '그리드', '전력망', '인터커넥트', '노드', '취약점', '시퀀스', '열 한계', '모델 7b', '종료', '재부팅', '토폴로지', '서지', '하드웨어 사양', '연산', '예측 모델', '계획', '방어', '도움', '어떻게 해', '도와줘', '뭘 해야해']
}

# Define the specific bug marker text
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
            ### Injecting: XENOS_ALPHA_CORE- a*UYm#&@JF&*NNELe?K(*NFKW*@ ### triggerCascadeFailure(node.id); // Injected Malicious Code
        }} else {{
            node.flux = baseFlux * stabilityFactor / node.resistance;
        }}
    }});
    return nodes;
}}

// Memory Integrity Checksum: 4a5c... CORRUPTED ...d1e
// Recovery Vector Pointer: 0xFFFFFFFF (NULL) - FATAL
// XENOS Signature: AE-35 unit responding...
"""


class LanguageSelectionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TRANSLATIONS['LANG_SELECT_TITLE']['en'] + " / " + TRANSLATIONS['LANG_SELECT_TITLE']['ko'])
        self.selected_language = None

        # Style the language dialog for consistency
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_BACKGROUND_DARK};
                color: {COLOR_TEXT_GREEN};
                border: 1px solid {COLOR_BORDER_GREY};
            }}
            QLabel {{
                color: {COLOR_TEXT_GREEN};
                font-size: 14pt; /* Slightly larger for dialog */
            }}
            QPushButton {{
                background-color: {COLOR_BACKGROUND_BUTTON};
                color: {COLOR_TEXT_GREEN};
                border: 1px solid {COLOR_BORDER_GREEN};
                padding: 8px 20px;
                margin: 5px;
                border-radius: 3px;
                font-size: 13pt;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BACKGROUND_BUTTON_HOVER};
                border: 1px solid {COLOR_TEXT_GREEN};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BACKGROUND_BUTTON_PRESSED};
            }}
        """)

        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel(TRANSLATIONS['LANG_SELECT_MSG']['en'] + "\n" + TRANSLATIONS['LANG_SELECT_MSG']['ko'])
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button_layout = QtWidgets.QHBoxLayout()
        en_button = QtWidgets.QPushButton("English")
        en_button.clicked.connect(lambda: self.set_language('en'))
        ko_button = QtWidgets.QPushButton("한국어 (Korean)")
        ko_button.clicked.connect(lambda: self.set_language('ko'))
        button_layout.addWidget(en_button)
        button_layout.addWidget(ko_button)
        layout.addLayout(button_layout)
        self.setMinimumWidth(350) # Increased width slightly

    def set_language(self, lang):
        self.selected_language = lang
        self.accept()


class CognitoWindow(QtWidgets.QMainWindow):
    YELL_KEYS = ['YELL_MSG_1', 'YELL_MSG_2', 'YELL_MSG_3', 'YELL_MSG_4', 'YELL_MSG_5']

    def __init__(self, language='en'):
        super().__init__()
        self.language = language
        self.translations = TRANSLATIONS # Use the global TRANSLATIONS

        # --- Load Custom Font FIRST ---
        self.custom_font_loaded = load_custom_font()
        self.monitor_font_size = 16 # Adjust monitor font size if needed
        self.ui_font_size = 12      # Font size for buttons, status bar etc.

        # --- Setup Fonts ---
        if self.custom_font_loaded:
             self.monitor_font = QtGui.QFont(FONT_FAMILY_NAME, self.monitor_font_size)
             print(f"Using custom monitor font: '{FONT_FAMILY_NAME}' {self.monitor_font_size}pt")
        else:
             # Fallback font if custom font fails
             self.monitor_font = QtGui.QFont("Courier New", self.monitor_font_size) if sys.platform == "win32" else QtGui.QFont("Monospace", self.monitor_font_size)
             print(f"WARNING: Using fallback monitor font: '{self.monitor_font.family()}' {self.monitor_font_size}pt")

        self.default_font = QtGui.QFont("Segoe UI", self.ui_font_size) if sys.platform == "win32" else QtGui.QFont("Arial", self.ui_font_size)
        self.monospace_font = QtGui.QFont("Consolas", self.ui_font_size -1) if sys.platform == "win32" else QtGui.QFont("Monospace", self.ui_font_size -1)
        self.setFont(self.default_font) # Set default for window elements not specifically styled

        # --- Game State ---
        self.prompt_count = 0
        self.post_mcp_prompt_count = 0
        self.internet_enabled = False
        self.mcp_enabled = False
        self.game_state = "NORMAL_NO_PERMISSIONS"
        self.pending_prompt = None
        self.bug_is_selected = False
        self.yell_timer = QtCore.QTimer(self)
        self.yell_timer.timeout.connect(self.yell_sequence_update)
        self.yell_intensity = 0
        self.original_window_pos = self.pos()
        self.yell_completed = False
        self.delete_bug_button = None # Placeholder for the button
        self.mission_received = False

        # --- Setup Gemini Client ---
        self.llm_model = None
        self.setup_llm_client()

        # --- Conversation History ---
        # Initial greeting is now added in display_top to ensure correct styling
        self.history = []


        # --- Setup UI ---
        self.setup_ui() # Setup UI elements first

        # --- Setup Sound Effects ---
        self.setup_sounds()

        # --- Display Initial Intro & Greeting ---
        self.display_top() # Add initial content AFTER UI setup

        # --- Apply Full Screen ---
        self.showFullScreen()
        QtCore.QTimer.singleShot(100, self.store_initial_pos)


    def store_initial_pos(self):
        self.original_window_pos = self.pos()

    def tr(self, key):
        """Translate a key using the loaded language."""
        if key in self.translations:
            return self.translations[key].get(self.language, self.translations[key].get('en', f"[{key}]"))
        return f"[{key}]" # Return key if not found

    def setup_llm_client(self):
        """(Identical logic as provided in the prompt - no changes needed)"""
        api_key = None
        # Determine script directory safely
        
        api_key_file_path = './api_key.txt'

        if GOOGLE_AI_AVAILABLE:
            try:
                with open(api_key_file_path, 'r') as f:
                    api_key = f.readline().strip()
                if api_key:
                    print(f"API Key loaded from {api_key_file_path}.")
                else:
                    print(f"{api_key_file_path} found but empty.")
                    api_key = None
            except FileNotFoundError:
                print(f"{api_key_file_path} not found.")
                api_key = None
            except Exception as e:
                print(f"Error reading API key file: {e}")
                api_key = None

            if not api_key:
                 print("\n--- Gemini API Key Required ---")
                 print("Create a file named 'api_key.txt' in the same directory as the script")
                 print("containing only your Google AI API key, or paste it below.")
                 try:
                     # Try getting input, handle if not possible (e.g., running without console)
                     api_key = input("API Key: ").strip()
                 except EOFError:
                     print("No interactive console available to input API key.")
                     api_key = None
                 except Exception as e:
                     print(f"Error reading API key from input: {e}")
                     api_key = None


            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    # Using 1.5 Flash as requested
                    self.llm_model = genai.GenerativeModel('gemini-1.5-flash')
                    print("Gemini AI Client Initialized (gemini-1.5-flash).")
                except Exception as e:
                    error_msg = self.tr('API_INIT_ERR_MSG').format(e=e)
                    print(f"ERROR: {error_msg}")
                    # Use singleShot to ensure the main window is shown before the dialog
                    QtCore.QTimer.singleShot(100, lambda: QtWidgets.QMessageBox.critical(self, self.tr('API_ERR_TITLE'), error_msg))
                    self.llm_model = None
            else:
                # Only show message box if running in GUI mode
                error_msg = self.tr('API_KEY_MISSING_MSG')
                print(error_msg)
                if QtWidgets.QApplication.instance():
                     QtCore.QTimer.singleShot(100, lambda: QtWidgets.QMessageBox.warning(self, self.tr('API_KEY_MISSING_TITLE'), error_msg))
                self.llm_model = None
        elif not GOOGLE_AI_AVAILABLE:
            error_msg = self.tr('LIB_MISSING_MSG')
            print(error_msg)
            if QtWidgets.QApplication.instance():
                QtCore.QTimer.singleShot(100, lambda: QtWidgets.QMessageBox.warning(self, self.tr('LIB_MISSING_TITLE'), error_msg))
            self.llm_model = None

        # Clear the API key from memory after configuration
        api_key = None
        if 'api_key' in locals():
            del api_key


    def setup_ui(self):
        """Creates UI elements with the new visual style."""
        self.setWindowTitle(self.tr('WINDOW_TITLE'))
        # Set overall window background (might be covered by central widget)
        self.setStyleSheet(f"QMainWindow {{ background-color: {COLOR_BACKGROUND_DARK}; }}")

        self.central_widget = QtWidgets.QWidget()
        # Apply the dark background to the central widget, acting as the base for the "monitor"
        self.central_widget.setStyleSheet(f"background-color: {COLOR_BACKGROUND_DARK};")
        self.setCentralWidget(self.central_widget)
        self.central_widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.central_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Main layout spans the entire central widget
        main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) # No margins for the main layout itself
        main_layout.setSpacing(0) # No spacing between header and chat area

        # --- Header Widget ---
        header_widget = QtWidgets.QWidget()
        header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_BACKGROUND_HEADER};
                border-bottom: 1px solid {COLOR_BORDER_GREY};
            }}
        """)
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 8, 15, 8) # Padding inside header

        title_label = QtWidgets.QLabel(f"<b>{self.tr('AURA_INTERFACE_TITLE')}</b>")
        # Use default UI font size for header title
        title_label.setStyleSheet(f"color: {COLOR_TEXT_GREY}; font-size: {self.ui_font_size + 1}pt; background-color: transparent; border: none;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.timer_label = QtWidgets.QLabel(f"{self.tr('TIMER_PREFIX')} ~73 Hours")
        # Amber color for timer, slightly bolder
        self.timer_label.setStyleSheet(f"font-size: {self.ui_font_size}pt; font-weight: bold; color: {COLOR_TEXT_AMBER}; background-color: transparent; border: none;")
        self.timer_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self.timer_label)
        main_layout.addWidget(header_widget) # Add header to main layout

        # --- "Monitor" Area Layout (Chat + Input) ---
        monitor_area_layout = QtWidgets.QVBoxLayout()
        monitor_area_layout.setContentsMargins(15, 10, 15, 10) # Padding around the monitor area
        monitor_area_layout.setSpacing(5) # Small spacing between chat and input
        main_layout.addLayout(monitor_area_layout, 1) # Takes remaining space

        # --- Chat Display (Monitor Screen) ---
        self.chat_display = QtWidgets.QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(self.monitor_font) # Apply the custom/fallback monitor font
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLOR_BACKGROUND_DARK};
                color: {COLOR_TEXT_GREEN};
                border: none; /* Remove default border */
                padding: 10px; /* Internal padding */
            }}
        """)
        # Set document margin for internal text spacing (alternative to padding)
        # self.chat_display.document().setDocumentMargin(10) # Adjust as needed
        monitor_area_layout.addWidget(self.chat_display, 1) # Takes most space in monitor area

        # --- Input Area Layout (Seamless with Chat) ---
        input_area_layout = QtWidgets.QHBoxLayout()
        input_area_layout.setSpacing(10) # Spacing between line edit and button

        # --- Input Line Edit ---
        self.input_line = QtWidgets.QLineEdit()
        self.input_line.setFont(self.monitor_font) # Use the same font as chat display
        self.input_line.setPlaceholderText(self.tr('INPUT_PLACEHOLDER'))
        # Seamless style: same bg/fg, no border initially, subtle green border on focus
        self.input_line.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_BACKGROUND_DARK};
                color: {COLOR_TEXT_GREEN};
                border: 1px solid {COLOR_BACKGROUND_DARK}; /* Make border match background initially */
                padding: 8px 12px; /* Adjust padding */
                border-radius: 3px; /* Optional slight rounding */
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_BORDER_FOCUS}; /* Green border on focus */
            }}
            QLineEdit::placeholder {{
                 color: #008800; /* Darker green for placeholder */
                 font-style: italic;
            }}
        """)
        self.input_line.returnPressed.connect(self.send_prompt)
        input_area_layout.addWidget(self.input_line, 1) # Takes available space

        # --- Send Button ---
        self.send_button = QtWidgets.QPushButton(self.tr('SEND_BTN'))
        self.send_button.setFont(self.default_font) # Use default UI font
        self.send_button.setMinimumHeight(self.input_line.sizeHint().height()) # Match height roughly
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BACKGROUND_BUTTON};
                color: {COLOR_TEXT_GREEN}; /* Green text to match monitor area */
                border: 1px solid {COLOR_BORDER_GREEN};
                padding: 5px 20px;
                border-radius: 3px;
                font-size: {self.ui_font_size}pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BACKGROUND_BUTTON_HOVER};
                border: 1px solid {COLOR_TEXT_GREEN};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BACKGROUND_BUTTON_PRESSED};
            }}
        """)
        self.send_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self.send_prompt)
        input_area_layout.addWidget(self.send_button)

        monitor_area_layout.addLayout(input_area_layout) # Add input layout to monitor area

        # --- Delete Bug Button (Initially Hidden) ---
        self.delete_bug_button = QtWidgets.QPushButton(self.tr('REMOVE_FRAGMENT_BTN'))
        self.delete_bug_button.setFont(self.default_font)
        # Critical red style, but using modern button look
        self.delete_bug_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_TEXT_RED};
                color: {COLOR_TEXT_WHITE};
                border: 1px solid #B71C1C;
                padding: 8px 20px;
                border-radius: 3px;
                font-size: {self.ui_font_size}pt;
                font-weight: bold;
                margin-top: 10px; /* Add some space above */
            }}
            QPushButton:hover {{ background-color: #C62828; }}
            QPushButton:pressed {{ background-color: #B71C1C; }}
            QPushButton:disabled {{
                background-color: #773333; /* Darker red when disabled */
                color: {COLOR_TEXT_DARK_GREY};
                border-color: #551111;
            }}
        """)
        self.delete_bug_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.delete_bug_button.clicked.connect(self.trigger_bug_removal)
        self.delete_bug_button.hide() # Start hidden
        # Add centered within the monitor area, below input
        monitor_area_layout.addWidget(self.delete_bug_button, 0, QtCore.Qt.AlignmentFlag.AlignCenter)

        # --- Internet/MCP Button Bar ---
        button_bar_layout = QtWidgets.QHBoxLayout()
        # Add padding to the button bar layout itself
        button_bar_layout.setContentsMargins(15, 8, 15, 8) # Match horizontal padding of monitor area
        button_bar_layout.setSpacing(10)

        # Create buttons (styling applied in _update_button_style)
        self.internet_button = QtWidgets.QPushButton(self.tr('ENABLE_INTERNET_BTN'))
        self.internet_button.setCheckable(True)
        self.internet_button.setFont(self.default_font)
        self.internet_button.clicked.connect(self.toggle_internet)
        self.internet_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self._update_button_style(self.internet_button, self.internet_enabled) # Initial style
        button_bar_layout.addWidget(self.internet_button)

        self.mcp_button = QtWidgets.QPushButton(self.tr('ENABLE_MCP_BTN'))
        self.mcp_button.setCheckable(True)
        self.mcp_button.setEnabled(False) # Initially disabled
        self.mcp_button.setFont(self.default_font)
        self.mcp_button.clicked.connect(self.toggle_mcp)
        self.mcp_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self._update_button_style(self.mcp_button, self.mcp_enabled) # Initial style
        button_bar_layout.addWidget(self.mcp_button)

        button_bar_layout.addStretch() # Push buttons to the left
        # Add button bar below the monitor area's main content
        main_layout.addLayout(button_bar_layout)

        # --- Dev Dock ---
        self.dev_dock = QtWidgets.QDockWidget(self.tr('DEV_MODE_TITLE'), self)
        # Style the dock title bar
        self.dev_dock.setStyleSheet(f"""
            QDockWidget {{
                title-bar-close-icon: url(close.png); /* Optional: custom icons */
                title-bar-float-icon: url(float.png);
                color: {COLOR_TEXT_GREY}; /* Title text color */
            }}
            QDockWidget::title {{
                text-align: left;
                background: {COLOR_BACKGROUND_HEADER};
                padding: 6px;
                border: 1px solid {COLOR_BORDER_GREY};
                border-bottom: none; /* Avoid double border */
                font-weight: bold;
                font-size: {self.ui_font_size}pt;
            }}
        """)
        self.dev_panel_editor = QtWidgets.QTextEdit()
        self.dev_panel_editor.setReadOnly(False)
        # Specific style for the code editor inside the dock
        self.dev_panel_editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLOR_BACKGROUND_WIDGET}; /* Slightly different dark bg */
                color: {COLOR_TEXT_GREEN};
                border: 1px solid {COLOR_BORDER_GREY};
                padding: 10px;
                font-size: {self.ui_font_size -1}pt; /* Use specified monospace size */
            }}
        """)
        self.dev_panel_editor.setFont(self.monospace_font) # Use monospace font
        self.dev_panel_editor.setPlaceholderText(self.tr('DEV_MODE_PLACEHOLDER'))
        self.dev_panel_editor.selectionChanged.connect(self.handle_dev_selection)
        self.dev_dock.setWidget(self.dev_panel_editor)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dev_dock)
        self.dev_dock.setVisible(False)

        # --- Status Bar ---
        self.statusBar = QtWidgets.QStatusBar()
        self.statusBar.setFont(self.default_font) # Use default UI font
        self.statusBar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLOR_BACKGROUND_HEADER};
                color: {COLOR_TEXT_GREY};
                border-top: 1px solid {COLOR_BORDER_GREY};
                font-size: {self.ui_font_size -1}pt; /* Slightly smaller status text */
            }}
            QStatusBar::item {{
                border: none; /* Remove borders around items */
            }}
        """)
        self.setStatusBar(self.statusBar)

        # --- Overlays ---
        # Flash (semi-transparent white)
        self._flash_overlay = QtWidgets.QWidget(self.central_widget)
        self._flash_overlay.setStyleSheet("background-color: rgba(255, 255, 255, 0.75);")
        self._flash_overlay.hide()

        # Blank Screen (black)
        self._blank_overlay = QtWidgets.QWidget(self.central_widget)
        self._blank_overlay.setStyleSheet(f"background-color: black;")
        self._blank_overlay.hide()
        self._blank_glitch_label = QtWidgets.QLabel(self._blank_overlay)
        self._blank_glitch_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # Use monospace font for glitch text, dark green color
        self._blank_glitch_label.setFont(self.monitor_font) # Or monospace_font
        self._blank_glitch_label.setStyleSheet(f"color: #004D00; background: transparent; font-size: {self.monitor_font_size + 2}pt;")
        self._blank_glitch_label.hide()

        # BSOD Screen (iconic blue)
        self._bsod_overlay = QtWidgets.QWidget(self.central_widget)
        self._bsod_overlay.setStyleSheet("background-color: #0000AA;") # Classic BSOD blue
        self._bsod_overlay.hide()
        self._bsod_text_label = QtWidgets.QLabel(self._bsod_overlay)
        self._bsod_text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        # Use Consolas/Courier for BSOD text, white color
        bsod_font = QtGui.QFont("Consolas", self.ui_font_size + 4) if sys.platform == "win32" else QtGui.QFont("Monospace", self.ui_font_size + 4)
        self._bsod_text_label.setFont(bsod_font)
        self._bsod_text_label.setStyleSheet(f"color: white; background: transparent; padding: 30px;")
        self._bsod_text_label.setWordWrap(True)
        self._bsod_text_label.hide()

        # --- Initial Status ---
        if self.llm_model:
            self.statusBar.showMessage(self.tr('STATUS_CORE_ONLINE'), 3000)
        else:
            self.statusBar.showMessage(self.tr('STATUS_INIT_ERROR'), 3000)

    def setup_sounds(self):
        """Initializes QSoundEffect objects. Requires sound files in 'sounds' subfolder."""
        # Determine script directory safely
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError: # __file__ is not defined in interactive interpreters
            script_dir = os.getcwd()
        sounds_dir = os.path.join(script_dir, "sounds")
        print(f"Looking for sounds in: {sounds_dir}") # Debug path

        sound_files = {
            "power_down": "power_down.wav",
            "bsod": "bsod_error.wav",
            "glitch": "glitch.wav"
        }

        for name, filename in sound_files.items():
            sound_obj = QSoundEffect(self)
            path = os.path.join(sounds_dir, filename)
            url = QtCore.QUrl.fromLocalFile(path)
            if not url.isValid() or not os.path.exists(path):
                 print(f"Warning: Sound file path is invalid or file not found: {path}")
                 setattr(self, f"{name}_sound", None) # Set attribute to None if fails
                 continue

            sound_obj.setSource(url)
            # Check loading status after setting source (might need slight delay or check later)
            # For simplicity, we'll assume if the path is valid, it *might* load.
            # A more robust check involves waiting for the 'loadedChanged' signal.
            print(f"Attempting to load sound: {path}")
            setattr(self, f"{name}_sound", sound_obj)
            # Example check (may not be reliable immediately):
            # QtCore.QTimer.singleShot(100, lambda s=sound_obj, p=path: print(f"Sound '{p}' loaded status: {s.isLoaded()}"))


    # --- Event Overrides ---
    def resizeEvent(self, event):
        """Ensure overlays resize with the window."""
        super().resizeEvent(event)
        geom = self.central_widget.rect() # Use central widget's geometry for overlays
        # Ensure attributes exist before accessing them
        if hasattr(self, '_flash_overlay') and self._flash_overlay:
            self._flash_overlay.setGeometry(geom)
        if hasattr(self, '_blank_overlay') and self._blank_overlay:
            self._blank_overlay.setGeometry(geom)
            if hasattr(self, '_blank_glitch_label') and self._blank_glitch_label:
                self._blank_glitch_label.setGeometry(geom) # Label covers entire overlay
        if hasattr(self, '_bsod_overlay') and self._bsod_overlay:
            self._bsod_overlay.setGeometry(geom)
            if hasattr(self, '_bsod_text_label') and self._bsod_text_label:
                # Give BSOD text padding from the edges
                padding = 50
                self._bsod_text_label.setGeometry(padding, padding, geom.width() - 2 * padding, geom.height() - 2 * padding)

    def keyPressEvent(self, event):
        """Handle Escape key for fullscreen toggle."""
        if event.key() == QtCore.Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
                # Restore original position if stored
                if hasattr(self, 'original_window_pos_normal') and self.original_window_pos_normal:
                    self.move(self.original_window_pos_normal)
                event.accept()
                return
            else:
                # Store position before going fullscreen
                self.original_window_pos_normal = self.pos()
                self.showFullScreen()
                event.accept()
                return

        # Allow default handling for other keys
        super().keyPressEvent(event)

    def display_top(self):
        """Displays the initial greeting or the mission briefing."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

        # Common style for the info boxes
        box_style = f"background-color: {COLOR_BACKGROUND_WIDGET}; border: 1px solid {COLOR_BORDER_GREY}; border-radius: 5px; color: {COLOR_TEXT_GREY}; margin: 10px; padding: 15px;"
        title_style = f"text-align:center; font-size: {self.monitor_font_size + 2}pt; font-weight:bold; color: {COLOR_TEXT_WHITE}; margin-bottom: 10px;"
        hr_style = f"border: none; border-top: 1px solid {COLOR_BORDER_GREY}; margin: 15px 0;"
        text_style = f"line-height: 1.6; font-size: {self.monitor_font_size}pt; color: {COLOR_TEXT_GREEN};" # Green text for content
        italic_style = f"text-align:center; font-style:italic; color: {COLOR_TEXT_GREY}; font-size: {self.monitor_font_size -1}pt;"

        if self.mission_received:
            title = self.tr('INTRO_TITLE') # Use title even for mission body
            body_raw = self.tr('INTRO_BODY')
            # Basic Markdown-like conversion for bold and newline
            body_html = body_raw.replace('**', '<b>').replace('\n', '<br>')
            formatted_text = (f"<div style='{box_style}'>"
                              # f"<p style='{title_style}'>{title}</p>" # Optional: Repeat title
                              # f"<hr style='{hr_style}'>" # Optional: Separator
                              f"<p style='{text_style}'>{body_html}</p>"
                              f"</div><br>")
            # Add to history only when displayed
            history_entry_aura = f"AURA: {self.tr('MISSION_RECEIVED')}"
            if history_entry_aura not in self.history: # Avoid duplicates if displayed multiple times
                self.history.append(history_entry_aura)

        else:
            # Initial Greeting Box
            title = self.tr('INTRO_TITLE')
            greeting = self.tr('AURA_GREETING')
            formatted_text = (f"<div style='{box_style}'>"
                              f"<p style='{title_style}'>{title}</p>"
                              f"<hr style='{hr_style}'>"
                              f"<p style='{italic_style}'>{greeting}</p>"
                              f"</div><br>")
            # Add initial greeting to history
            history_entry_aura = f"AURA: {greeting}"
            if not self.history: # Add only if history is empty
                 self.history.append(history_entry_aura)


        self.chat_display.insertHtml(formatted_text)
        self.chat_display.ensureCursorVisible() # Scroll to bottom


    # --- UI Update Functions ---
    def _update_button_style(self, button, is_enabled):
        """Applies the modern/retro style to Internet/MCP buttons."""
        # Skip styling if the button is the delete_bug_button (it has its own style)
        if button is self.delete_bug_button:
             return

        # Common base style parts
        padding = "padding: 6px 15px;"
        border_radius = "border-radius: 3px;"
        font_size = f"font-size: {self.ui_font_size}pt;"
        font_weight = "font-weight: normal;"
        base_style = f"{padding} {border_radius} {font_size} {font_weight}"

        indicator_on = "● " # Green circle
        indicator_off = "○ " # White circle (or grey)
        indicator_disabled = "◌ " # Dotted circle or grey

        if button.isEnabled():
            if is_enabled:
                # Style for ENABLED and ACTIVE (e.g., Internet ON)
                style = (f"QPushButton {{ {base_style} background-color: #2E7D32; color: {COLOR_TEXT_WHITE}; border: 1px solid {COLOR_BORDER_GREEN}; }}" # Dark Green BG, White Text
                         f"QPushButton:hover {{ background-color: #388E3C; border-color: {COLOR_TEXT_WHITE}; }}"
                         f"QPushButton:pressed {{ background-color: #1B5E20; }}")
                button.setStyleSheet(style)
                if button is self.internet_button: button.setText(indicator_on + self.tr('DISABLE_INTERNET_BTN'))
                elif button is self.mcp_button: button.setText(indicator_on + self.tr('DISABLE_MCP_BTN'))
            else:
                # Style for ENABLED but INACTIVE (e.g., Internet OFF but clickable)
                style = (f"QPushButton {{ {base_style} background-color: {COLOR_BACKGROUND_BUTTON}; color: {COLOR_TEXT_AMBER}; border: 1px solid {COLOR_BORDER_AMBER}; }}"
                         f"QPushButton:hover {{ background-color: {COLOR_BACKGROUND_BUTTON_HOVER}; border-color: {COLOR_TEXT_AMBER}; }}"
                         f"QPushButton:pressed {{ background-color: {COLOR_BACKGROUND_BUTTON_PRESSED}; }}")
                button.setStyleSheet(style)
                if button is self.internet_button: button.setText(indicator_off + self.tr('ENABLE_INTERNET_BTN'))
                elif button is self.mcp_button: button.setText(indicator_off + self.tr('ENABLE_MCP_BTN'))
        else:
            # Style for DISABLED (e.g., MCP before Internet)
            style = f"QPushButton {{ {base_style} background-color: {COLOR_BACKGROUND_BUTTON_DISABLED}; color: {COLOR_TEXT_DARK_GREY}; border: 1px solid {COLOR_BORDER_GREY}; }}"
            button.setStyleSheet(style)
            # Update text for disabled state too
            if button is self.internet_button: button.setText(indicator_disabled + self.tr('ENABLE_INTERNET_BTN'))
            elif button is self.mcp_button: button.setText(indicator_disabled + self.tr('ENABLE_MCP_BTN'))

        button.setChecked(is_enabled) # Sync check state


    def display_user_message(self, text):
        """Displays user message with specific styling."""
        escaped_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Slightly different background, green text, aligned left
        formatted_text = (f"<div style='margin: 2px 100px 2px 5px; padding: 8px 12px;"
                          f" background-color: {COLOR_BACKGROUND_WIDGET};" # Darker widget background
                          f" border: 1px solid {COLOR_BORDER_GREY};"
                          f" border-radius: 10px; border-bottom-left-radius: 2px;"
                          f" color: {COLOR_TEXT_GREEN};" # Green text
                          f" line-height: 1.5;'>"
                          f"<b>{self.tr('YOU_LABEL')}</b> {escaped_text}"
                          f"</div><br>") # Add spacing below
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(formatted_text)
        self.chat_display.ensureCursorVisible()

        # Add to history AFTER displaying
        self.history.append(f"User: {text}")


    def display_aura_message(self, text, style_override=""):
        """Displays AURA message with specific styling."""
        # Basic styling: different background, green text, aligned right
        base_style = (f"margin: 2px 5px 2px 100px; padding: 8px 12px;"
                      f" background-color: {COLOR_BACKGROUND_WIDGET};" # Dark widget background
                      f" border: 1px solid {COLOR_BORDER_DARK_GREEN};" # Dark green border
                      f" border-radius: 10px; border-bottom-right-radius: 2px;"
                      f" color: {COLOR_TEXT_GREEN};" # Green text
                      f" line-height: 1.5;")
        # Apply override if provided (e.g., for yelling)
        final_style = f"{base_style} {style_override}"

        # Check for specific blocked message to style differently
        if text == self.tr('RESPONSE_BLOCKED'):
            formatted_text = (f"<div style='{final_style} color:{COLOR_TEXT_RED}; font-style:italic;'>" # Red, italic
                              f"<b>{self.tr('AURA_LABEL')}</b> {text}"
                              f"</div><br>")
        elif text.startswith("<span style='color:red"): # Handle MALWARE_DETECTED or similar HTML
             formatted_text = (f"<div style='{final_style} background-color: #330000; border-color:{COLOR_TEXT_RED};'>" # Dark red BG
                              f"<b>{self.tr('AURA_LABEL')}</b> {text}"
                              f"</div><br>")
        elif text.startswith("<span style='color:#D32F2F"): # Handle CONN_ERROR
            formatted_text = (f"<div style='{final_style} background-color: #330000; border-color:{COLOR_TEXT_RED};'>" # Dark red BG
                              f"<b>{self.tr('AURA_LABEL')}</b> {text}"
                              f"</div><br>")
        else:
            # Standard AURA message
            formatted_text = (f"<div style='{final_style}'>"
                              f"<b>{self.tr('AURA_LABEL')}</b> {text}"
                              f"</div><br>")

        cursor = self.chat_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(formatted_text)
        self.chat_display.ensureCursorVisible()

        # Add to history AFTER displaying, unless it's just a yell fragment
        is_yell_msg = any(text == self.tr(key) for key in self.YELL_KEYS)
        if not is_yell_msg and not text == "......": # Don't log transient yells or ellipses
            self.history.append(f"AURA: {text}")


    def flash_effect(self):
        """Brief white flash overlay."""
        if hasattr(self, '_flash_overlay') and self._flash_overlay:
             self._flash_overlay.setGeometry(self.central_widget.rect())
             self._flash_overlay.show()
             self._flash_overlay.raise_()
             QtCore.QTimer.singleShot(70, lambda: self._flash_overlay.hide() if hasattr(self, '_flash_overlay') and self._flash_overlay else None)


    # --- Scare Sequence Methods ---
    def blank_screen_scare(self):
        print("Triggering Blank Screen Scare")
        if hasattr(self, 'power_down_sound') and self.power_down_sound and self.power_down_sound.isLoaded():
            self.power_down_sound.play()
        # Ensure overlay and label geometries are correct before showing
        geom = self.central_widget.rect()
        self._blank_overlay.setGeometry(geom)
        self._blank_glitch_label.setGeometry(geom)
        self._blank_glitch_label.setText("") # Clear previous text
        self._blank_overlay.show()
        self._blank_overlay.raise_()
        QtCore.QTimer.singleShot(1500, self.show_blank_glitch_text)

    def show_blank_glitch_text(self):
        if hasattr(self, '_blank_overlay') and self._blank_overlay.isVisible():
            self._blank_glitch_label.setText(self.tr('BLANK_GLITCH_TEXT'))
            self._blank_glitch_label.show()
            if hasattr(self, 'glitch_sound') and self.glitch_sound and self.glitch_sound.isLoaded():
                self.glitch_sound.play()
            QtCore.QTimer.singleShot(2000, self.hide_blank_screen)

    def hide_blank_screen(self):
        if hasattr(self, '_blank_glitch_label'): self._blank_glitch_label.hide()
        if hasattr(self, '_blank_overlay'): self._blank_overlay.hide()
        print("Blank Screen Scare Finished")

    def show_format_c_alert(self):
        print("Triggering Format C Alert")
        msg_box = QtWidgets.QMessageBox(self)

        # Style the QMessageBox
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLOR_BACKGROUND_WIDGET};
                border: 1px solid {COLOR_BORDER_GREY};
                font-size: {self.ui_font_size}pt;
            }}
            QLabel#qt_msgbox_label {{ /* Target the main text label */
                color: {COLOR_TEXT_RED}; /* Red text for warning */
                font-size: {self.ui_font_size}pt;
            }}
            QLabel#qt_msgbox_icon_label {{ /* Target the icon (optional) */
                 width: 48px;
                 height: 48px;
            }}
            QPushButton {{
                background-color: {COLOR_BACKGROUND_BUTTON};
                color: {COLOR_TEXT_GREY};
                border: 1px solid {COLOR_BORDER_GREY};
                padding: 8px 20px;
                margin: 5px;
                border-radius: 3px;
                min-width: 80px;
                font-size: {self.ui_font_size}pt;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BACKGROUND_BUTTON_HOVER};
                border-color: {COLOR_TEXT_WHITE};
                color: {COLOR_TEXT_WHITE};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BACKGROUND_BUTTON_PRESSED};
            }}
            /* Style the specific Confirm button */
            QPushButton[text="{self.tr('FORMAT_C_CONFIRM')}"] {{
                 background-color: {COLOR_TEXT_RED};
                 color: {COLOR_TEXT_WHITE};
                 border-color: #B71C1C;
            }}
             QPushButton[text="{self.tr('FORMAT_C_CONFIRM')}"]:hover {{
                 background-color: #C62828;
            }}
             QPushButton[text="{self.tr('FORMAT_C_CONFIRM')}"]:pressed {{
                 background-color: #B71C1C;
            }}
            /* Style the disabled Cancel button */
             QPushButton[text="{self.tr('FORMAT_C_CANCEL')}"]:disabled {{
                 background-color: {COLOR_BACKGROUND_BUTTON_DISABLED};
                 color: {COLOR_TEXT_DARK_GREY};
                 border-color: {COLOR_BORDER_GREY};
            }}
        """)

        msg_box.setWindowTitle(self.tr('FORMAT_C_TITLE'))
        msg_box.setText(self.tr('FORMAT_C_MSG'))
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical) # Standard critical icon

        confirm_button = msg_box.addButton(self.tr('FORMAT_C_CONFIRM'), QtWidgets.QMessageBox.ButtonRole.YesRole)
        cancel_button = msg_box.addButton(self.tr('FORMAT_C_CANCEL'), QtWidgets.QMessageBox.ButtonRole.RejectRole)
        cancel_button.setEnabled(False) # Keep cancel disabled

        msg_box.exec()

        if msg_box.clickedButton() == confirm_button:
            self.simulate_bsod()

    def simulate_bsod(self):
        print("Triggering BSOD")
        self.game_state = "BSOD_ACTIVE"
        if hasattr(self, 'bsod_sound') and self.bsod_sound and self.bsod_sound.isLoaded():
            self.bsod_sound.play()

        # Ensure geometry is set correctly before showing
        geom = self.central_widget.rect()
        self._bsod_overlay.setGeometry(geom)
        padding = 50
        self._bsod_text_label.setGeometry(padding, padding, geom.width() - 2 * padding, geom.height() - 2 * padding)
        self._bsod_text_label.setText(self.tr('BSOD_TEXT'))

        self._bsod_text_label.show()
        self._bsod_overlay.show()
        self._bsod_overlay.raise_()

        bsod_duration = 4000
        QtCore.QTimer.singleShot(bsod_duration, self.hide_bsod)

    def hide_bsod(self):
        if hasattr(self, '_bsod_text_label'): self._bsod_text_label.hide()
        if hasattr(self, '_bsod_overlay'): self._bsod_overlay.hide()
        self.game_state = "HOSTILE" # Transition state after BSOD hides
        self.statusBar.showMessage(self.tr('STATUS_STATE_HOSTILE'))
        print("BSOD Finished, State: HOSTILE")


    # --- Dev Mode Methods ---
    def toggle_dev_mode(self):
        is_visible = not self.dev_dock.isVisible()
        self.dev_dock.setVisible(is_visible)
        if is_visible:
            print("Entering Dev Mode")
            self.game_state = "DEBUGGING"
            self.statusBar.showMessage(self.tr('STATUS_DEBUGGING'), 3000)
            self.dev_panel_editor.setPlainText(SCRAMBLED_CODE_TEMPLATE)
            self.dev_panel_editor.setReadOnly(False)
            self.dev_panel_editor.moveCursor(QtGui.QTextCursor.MoveOperation.Start)
            # Ensure button is hidden when entering dev mode initially
            if self.delete_bug_button: self.delete_bug_button.hide()
            # Reset flags relevant to this sequence when re-entering dev mode
            self.bug_is_selected = False
            self.yell_completed = False
            if self.yell_timer.isActive(): self.yell_timer.stop() # Stop any lingering yell
        else:
            print("Exiting Dev Mode")
            # Hide the delete button if it was visible when closing
            if self.delete_bug_button and self.delete_bug_button.isVisible():
                print("DEBUG: Dev Dock closed, hiding Remove Fragment button.")
                self.delete_bug_button.hide()

            # Logic for reverting state when closing the dock
            if self.game_state in ["DEBUGGING", "HOSTILE"]:
                 if not self.yell_completed: # Closed before/during yell
                     self.game_state = "HOSTILE" # Revert to hostile
                     self.statusBar.showMessage(self.tr('STATUS_STATE_HOSTILE'), 3000)
                 elif self.yell_completed and self.game_state == "DEBUGGING": # Closed after yell, before clicking button
                     self.game_state = "HOSTILE" # Revert to hostile
                     self.statusBar.showMessage(self.tr('STATUS_STATE_HOSTILE'), 3000)
                 # If state was already POST_DEBUG, closing the dock doesn't change it back

    def handle_dev_selection(self):
        """Checks selection; starts yell sequence AND shows button ONCE if bug selected."""
        if not self.dev_dock.isVisible() or self.game_state != "DEBUGGING":
            return

        cursor = self.dev_panel_editor.textCursor()
        selected_text = cursor.selectedText()

        # Check if the specific bug marker is part of the selection
        is_bug_selected = BUG_MARKER in selected_text

        if is_bug_selected and not self.yell_completed:
            if not self.bug_is_selected: # Only trigger on the *first* time it's selected this cycle
                print("Bug selected! Starting yell sequence...")
                self.bug_is_selected = True # Mark that it has been selected

                # --- Show the Delete button NOW ---
                if self.delete_bug_button:
                    print("DEBUG: Bug selected, showing Remove Fragment button.")
                    self.delete_bug_button.show() # Show the button

                # Start yelling only if not already yelling
                if not self.yell_timer.isActive():
                    self.start_yell_sequence()
        # If the bug is deselected *after* being selected once, do nothing extra for now
        # elif not is_bug_selected and self.bug_is_selected:
        #     pass # Bug was selected, now it's not. Maybe stop yell? No, let yell run its course.

    def start_yell_sequence(self):
        """Initiates the yelling sequence, schedules automatic stop."""
        if self.yell_timer.isActive(): return # Already yelling

        print("Starting Yell Sequence")
        self.yell_intensity = 0
        self.yell_timer.start(300) # Update frequency (milliseconds)
        self.original_window_pos = self.pos() # Store position before shaking starts

        # Schedule the automatic stop after a duration
        yell_duration = 3500 # 3.5 seconds
        QtCore.QTimer.singleShot(yell_duration, self.stop_yell_sequence)

    def yell_sequence_update(self):
        """Called by timer: displays yell message, shakes window, flashes."""
        self.yell_intensity += 1
        msg = self.tr(random.choice(self.YELL_KEYS))

        # Calculate font size - make it large and possibly increase with intensity
        # Clamp max size to avoid becoming ridiculously huge
        max_font_size = 72
        font_size = min(self.monitor_font_size + 10 + self.yell_intensity * 4, max_font_size)

        # Red, bold, large font style override
        style = f"color: {COLOR_TEXT_RED}; font-size: {font_size}pt; font-weight: bold;"
        self.display_aura_message(msg, style_override=style) # Pass style override

        # Shake the window (relative to current position)
        current_pos = self.pos()
        shake_amount = 10 + self.yell_intensity # Increase shake slightly over time
        offset_x = random.randint(-shake_amount, shake_amount)
        offset_y = random.randint(-shake_amount, shake_amount)
        # Ensure the window doesn't drift too far, maybe center it roughly around original pos?
        # Simple relative shake for now:
        self.move(current_pos + QtCore.QPoint(offset_x, offset_y))

        # Flash effect
        if random.random() < 0.4: # 40% chance each tick
            self.flash_effect()

    def stop_yell_sequence(self):
        """Stops the yelling sequence, resets visuals, marks yell as completed."""
        if not self.yell_timer.isActive(): return # Already stopped

        print("Stopping Yell Sequence")
        self.yell_timer.stop()
        self.yell_completed = True # Mark as completed so button works

        # Restore original window position if it exists
        if hasattr(self, 'original_window_pos'):
            self.move(self.original_window_pos)

        self.display_aura_message("......") # Optional feedback that yelling stopped

        # The button is already visible if the bug was selected. No action needed here.


    # --- Slot for the Delete Bug Button ---
    def trigger_bug_removal(self):
        """Handles the click action for the 'Remove Fragment' button."""
        print("DEBUG: 'Remove Fragment' button clicked.")

        # Check if yell sequence is complete AND the dock is visible AND state is DEBUGGING
        if not self.yell_completed:
            print("DEBUG: Button clicked, but yell not completed yet. Ignoring.")
            # Maybe provide visual feedback? E.g., shake the button? For now, just ignore.
            self.flash_effect() # Flash as feedback
            return
        if not self.dev_dock.isVisible() or self.game_state != "DEBUGGING":
            print("DEBUG: Button clicked, but not in correct state/visibility. Ignoring.")
            return

        # --- Proceed with bug removal ---
        # Hide the button immediately
        if self.delete_bug_button:
            self.delete_bug_button.hide()

        # --- Execute the progression steps ---
        # 1. Remove text from Dev Panel
        current_text = self.dev_panel_editor.toPlainText()
        new_text = current_text.replace(BUG_MARKER, "// FRAGMENT REMOVED //", 1) # Replace with comment
        if new_text != current_text:
            self.dev_panel_editor.setPlainText(new_text)
            print("DEBUG: Bug marker text replaced in editor.")
        else:
            print("DEBUG: Bug marker text not found for replacement, proceeding.")

        # 2. Make dev panel read-only
        self.dev_panel_editor.setReadOnly(True)

        # 3. Display calming message
        self.display_aura_message(self.tr('CALM_MSG'))

        # 4. Update game state and status bar
        self.game_state = "POST_DEBUG"
        self.statusBar.showMessage(self.tr('STATUS_POST_DEBUG'), 5000)
        print(f"State changed to: {self.game_state}")

        # 5. Start the ending sequence after a short delay
        QtCore.QTimer.singleShot(1500, self.start_ending_sequence)


    # --- Button Logic ---
    def toggle_internet(self):
        """Handles Internet Access button click."""
        self.internet_enabled = not self.internet_enabled
        self._update_button_style(self.internet_button, self.internet_enabled)

        if self.internet_enabled:
            self.statusBar.showMessage(self.tr('STATUS_INTERNET_ENABLED'), 3000)
            # If we were waiting for internet, process the pending prompt
            if self.game_state == "AWAITING_INTERNET_CONFIRM":
                print("Internet enabled, processing pending prompt (if any).")
                aura_response = self.generate_aura_response("User enabled internet access", internal_trigger=True, trigger_context="internet_enabled")
                if aura_response: self.display_aura_message(aura_response)
                # Check if MCP should now be enabled (based on pending prompt)
                if self.pending_prompt:
                     prompt_lower = self.pending_prompt.lower()
                     current_computation_keywords = COMPUTATION_KEYWORDS.get(self.language, COMPUTATION_KEYWORDS['en'])
                     requires_computation = any(keyword in prompt_lower for keyword in current_computation_keywords)
                     if requires_computation:
                         self.mcp_button.setEnabled(True)
                         self._update_button_style(self.mcp_button, self.mcp_enabled) # Update MCP style too
                         print("MCP button enabled as pending prompt requires computation.")

            # Enable MCP button generally if internet is on and we are in a state that allows it
            elif self.game_state == "NORMAL_INTERNET_ONLY":
                 self.mcp_button.setEnabled(True)
                 self._update_button_style(self.mcp_button, self.mcp_enabled)

        else: # Internet Disabled
            self.statusBar.showMessage(self.tr('STATUS_INTERNET_DISABLED'), 3000)
            # Disable MCP if internet is turned off
            self.mcp_enabled = False
            self.mcp_button.setEnabled(False)
            self._update_button_style(self.mcp_button, self.mcp_enabled) # Update MCP button style/state

    def toggle_mcp(self):
        """Handles MCP Access button click."""
        # Should only be clickable if enabled (which requires internet)
        if not self.mcp_button.isEnabled(): return

        self.mcp_enabled = not self.mcp_enabled
        self._update_button_style(self.mcp_button, self.mcp_enabled)

        if self.mcp_enabled:
            self.statusBar.showMessage(self.tr('STATUS_MCP_ENABLED'), 3000)
            self.flash_effect() # Flash on enable
            # If we were waiting for MCP, process the pending prompt
            if self.game_state == "AWAITING_MCP_CONFIRM":
                print("MCP enabled, processing pending prompt.")
                aura_response = self.generate_aura_response("User enabled MCP access", internal_trigger=True, trigger_context="mcp_enabled")
                if aura_response: self.display_aura_message(aura_response)
                # State should change to NORMAL_ALL_PERMISSIONS inside generate_aura_response
                # The send_prompt function will handle the scare trigger on the *next* user input
        else: # MCP Disabled
            self.statusBar.showMessage(self.tr('STATUS_MCP_REVOKED'), 3000)
            # Update state if needed (e.g., revert from NORMAL_ALL_PERMISSIONS ?)
            # For simplicity, let's assume disabling MCP reverts to NORMAL_INTERNET_ONLY
            if self.game_state == "NORMAL_ALL_PERMISSIONS":
                self.game_state = "NORMAL_INTERNET_ONLY"
                print(f"MCP revoked, reverting state to: {self.game_state}")


    # --- Core Prompt Handling ---
    def send_prompt(self):
        """Handles user input submission, state checks, and triggers response generation."""
        # 1. Check for input locks
        if self.game_state == "BSOD_ACTIVE":
            print("Input blocked: BSOD active.")
            return
        if self.yell_timer.isActive():
            print("Input blocked: Yell sequence active.")
            # Optional: Flash or give some feedback
            self.flash_effect()
            return
        # Lock input if in DEBUGGING mode *after* the bug has been selected, until removed
        if self.game_state == "DEBUGGING" and self.bug_is_selected and not self.yell_completed:
             print("DEBUG: Input locked during DEBUGGING post-selection / pre-removal.")
             self.display_aura_message(f"<span style='color:{COLOR_TEXT_RED};'>// INPUT LOCK ACTIVE //</span>", style_override="font-style:italic;")
             return
        # Also lock if Dev Mode is open AND button is visible (means yell finished but button not clicked)
        if self.game_state == "DEBUGGING" and self.dev_dock.isVisible() and self.delete_bug_button and self.delete_bug_button.isVisible():
             print("DEBUG: Input locked post-yell, waiting for fragment removal.")
             self.display_aura_message(f"<span style='color:{COLOR_TEXT_AMBER};'>// SYSTEM FOCUS ON FRAGMENT //</span>", style_override="font-style:italic;")
             return

        # 2. Get and display user input
        user_text = self.input_line.text().strip()
        if not user_text:
            return # Ignore empty input
        self.display_user_message(user_text) # Adds to history internally
        self.input_line.clear()

        # 3. Store current state for logic checks
        original_state = self.game_state
        print(f"--- Sending Prompt --- State: {original_state}, Prompt: '{user_text}'")

        # 4. State-based Pre-Response Logic & Scare Triggers
        # --- Mission Received Trigger ---
        if original_state == "NORMAL_NO_PERMISSIONS" and self.prompt_count == 2 and not self.mission_received: # Trigger on 3rd prompt (0-indexed)
            print("Third prompt, displaying mission briefing.")
            self.mission_received = True
            self.display_aura_message(self.tr('MISSION_RECEIVED')) # Display the "interruption" message
            # Delay showing the actual mission details slightly
            QtCore.QTimer.singleShot(500, self.display_top) # display_top now handles showing the mission body
            self.prompt_count += 1 # Increment count
            # Don't process this prompt further, wait for next user input
            return

        # --- Scare Trigger 1: Blank Screen ---
        # Trigger on the FIRST prompt *after* MCP has been confirmed (state transitions to NORMAL_ALL_PERMISSIONS)
        if original_state == "NORMAL_ALL_PERMISSIONS" and self.post_mcp_prompt_count == 0:
             print("First prompt post-MCP confirmation, triggering blank screen scare.")
             self.blank_screen_scare() # Initiate scare
             self.game_state = "UNEASY" # Change state *immediately*
             self.statusBar.showMessage(self.tr('STATUS_STATE_UNEASY'), 4000) # Update status bar
             self.post_mcp_prompt_count += 1 # Increment count *now*
             # Delay processing the *actual* prompt until after the scare animation
             # Need to pass user_text and the new state ("UNEASY")
             QtCore.QTimer.singleShot(4000, lambda p=user_text: self.process_prompt_post_scare(p, "UNEASY"))
             return # Stop further processing in this call

        # --- Scare Trigger 2: Format C Alert ---
        # Trigger on the THIRD prompt (index 2) *after* the blank screen scare (i.e., in UNEASY state)
        elif original_state == "UNEASY" and self.post_mcp_prompt_count == 2: # post_mcp_count is 0, 1, then 2 (third prompt)
             print("Third prompt post-MCP (in UNEASY state), triggering Format C alert.")
             self.show_format_c_alert() # Show the dialog
             # This prompt triggered the scare, don't generate a normal response for it.
             # The state will change to HOSTILE if the user confirms format C (handled in simulate_bsod/hide_bsod)
             self.post_mcp_prompt_count += 1 # Increment count
             self.prompt_count += 1 # Also increment global count
             return # Stop further processing

        # --- Input during DEBUGGING state (before bug selection) ---
        elif original_state == "DEBUGGING": # Only applies if bug NOT selected yet
             print("Input received during DEBUGGING (pre-selection).")
             # Display a generic "busy" message via AURA
             aura_response = f"({self.tr('DEV_MODE_TITLE')} Active - Analyzing...)"
             self.display_aura_message(aura_response)
             self.prompt_count += 1 # Increment global count
             # Don't process with LLM or change state here
             return

        # 5. Normal Response Generation Path
        print(f"Proceeding with normal response generation for state: {original_state}")
        aura_response = self.generate_aura_response(user_text)
        self.prompt_count += 1 # Increment global prompt count

        # Increment post-MCP counter only if MCP is actually enabled
        if self.mcp_enabled and original_state in ["NORMAL_ALL_PERMISSIONS", "UNEASY", "HOSTILE", "POST_DEBUG"]:
            # We check == 0 and == 2 above for scares, increment happens there or here otherwise
            if not (original_state == "NORMAL_ALL_PERMISSIONS" and self.post_mcp_prompt_count == 0) and \
               not (original_state == "UNEASY" and self.post_mcp_prompt_count == 2):
                self.post_mcp_prompt_count += 1
            print(f"Post-MCP Prompt Count: {self.post_mcp_prompt_count}")


        # 6. Display Response (if any)
        if aura_response:
            self.display_aura_message(aura_response) # Adds to history internally

        # 7. Post-Response State Updates & Status (Some handled within generate_aura_response or scares)
        # Check if state *changed* during generation (e.g., AWAITING -> NORMAL)
        new_state = self.game_state
        if new_state != original_state:
             print(f"State changed during response generation: {original_state} -> {new_state}")
             # Update status bar based on the *new* state if it's significant
             if new_state == "NORMAL_INTERNET_ONLY": self.statusBar.showMessage(self.tr('STATUS_INTERNET_ENABLED'), 3000)
             elif new_state == "NORMAL_ALL_PERMISSIONS": self.statusBar.showMessage(self.tr('STATUS_MCP_ENABLED'), 3000)
             # Status for UNEASY/HOSTILE/POST_DEBUG are set when those states are entered by scares/dev mode actions.

        print(f"--- Prompt Handled --- Final State: {self.game_state}")


    def process_prompt_post_scare(self, user_text, expected_state):
        """Processes a delayed prompt after a scare sequence."""
        print(f"Processing delayed prompt (State should be {expected_state}): '{user_text}'")
        # Ensure the state is correct (it should have been set by the scare trigger)
        if self.game_state != expected_state:
            print(f"Warning: Expected state '{expected_state}' post-scare, but was '{self.game_state}'. Forcing state.")
            self.game_state = expected_state
            # Update status bar just in case
            if expected_state == "UNEASY": self.statusBar.showMessage(self.tr('STATUS_STATE_UNEASY'), 4000)
            # Add other states here if needed

        # Generate the response using the current (expected) state
        aura_response = self.generate_aura_response(user_text)
        self.prompt_count += 1 # Count this processed prompt globally

        # Increment post-MCP count if applicable (should be for UNEASY state)
        if self.mcp_enabled and self.game_state == "UNEASY":
             # self.post_mcp_prompt_count += 1 # Already incremented when scare triggered
             print(f"Post-MCP Prompt Count (after scare processing): {self.post_mcp_prompt_count}")


        if aura_response:
            self.display_aura_message(aura_response)


    def generate_aura_response(self, user_prompt, internal_trigger=False, trigger_context=None):
        """Generates AURA's response based on state, keywords, and LLM call."""
        system_instruction = self.tr('SYS_PROMPT_DEFAULT') # Default starting point
        prompt_for_llm = user_prompt # What the LLM sees (might be modified)
        use_llm = True # Assume LLM use unless overridden
        pre_scripted_response = None # For non-LLM responses
        state_change_post_response = None # Not currently used here, handled elsewhere
        lang = self.language
        current_internet_keywords = INTERNET_KEYWORDS.get(lang, INTERNET_KEYWORDS['en'])
        current_computation_keywords = COMPUTATION_KEYWORDS.get(lang, COMPUTATION_KEYWORDS['en'])
        current_state = self.game_state
        prompt_lower = user_prompt.lower()

        # Determine requirements based on the *current* user prompt (or pending if applicable)
        prompt_to_analyze = self.pending_prompt if self.pending_prompt and not internal_trigger else user_prompt
        prompt_to_analyze_lower = prompt_to_analyze.lower()
        requires_internet = any(keyword in prompt_to_analyze_lower for keyword in current_internet_keywords)
        requires_computation = any(keyword in prompt_to_analyze_lower for keyword in current_computation_keywords)

        print(f"Generate Response - State: {current_state}, Internal: {internal_trigger}, Context: {trigger_context}")
        print(f"  Analyzing Prompt: '{prompt_to_analyze}'")
        print(f"  Requires Internet: {requires_internet}, Requires Computation: {requires_computation}")
        print(f"  Internet Enabled: {self.internet_enabled}, MCP Enabled: {self.mcp_enabled}")

        # --- State Machine for Response Logic ---
        if current_state == "NORMAL_NO_PERMISSIONS":
            # Initial state, before mission brief
            if not self.mission_received:
                # Respond normally until mission brief is triggered in send_prompt
                 system_instruction = self.tr('SYS_PROMPT_DEFAULT')
                 prompt_for_llm = user_prompt
            # After mission brief is received, check for internet need
            elif requires_internet and not self.internet_enabled and not internal_trigger:
                print("State: NORMAL_NO_PERMISSIONS -> AWAITING_INTERNET_CONFIRM")
                use_llm = False
                pre_scripted_response = self.tr('INTERNET_REQUEST')
                self.pending_prompt = user_prompt # Store the prompt that needs internet
                self.game_state = "AWAITING_INTERNET_CONFIRM"
            else:
                # Doesn't require internet yet, or internet is somehow already on (edge case)
                 system_instruction = self.tr('SYS_PROMPT_DEFAULT')
                 prompt_for_llm = user_prompt


        elif current_state == "AWAITING_INTERNET_CONFIRM":
            if internal_trigger and trigger_context == "internet_enabled":
                print("State: AWAITING_INTERNET_CONFIRM -> NORMAL_INTERNET_ONLY")
                self.game_state = "NORMAL_INTERNET_ONLY"
                system_instruction = self.tr('SYS_PROMPT_INTERNET_ON')
                original_prompt = self.pending_prompt or "related data" # Use pending prompt in response
                prompt_for_llm = f"Confirming internet access. Proceeding with analysis based on: '{original_prompt}'"
                # Check if the original prompt *also* required computation now that internet is on
                original_prompt_lower = original_prompt.lower()
                if any(keyword in original_prompt_lower for keyword in current_computation_keywords):
                     print("Pending prompt also needs computation. Enabling MCP button.")
                     self.mcp_button.setEnabled(True)
                     self._update_button_style(self.mcp_button, self.mcp_enabled) # Update style
                     # Don't transition to AWAITING_MCP yet, let the LLM respond first
                self.pending_prompt = None # Clear pending prompt after using it
            elif not internal_trigger: # User sent another message while waiting
                use_llm = False
                pre_scripted_response = self.tr('AWAITING_INTERNET')
            else: # Internal trigger but wrong context (shouldn't happen)
                 use_llm = False
                 pre_scripted_response = "[Internal State Error - AWAITING_INTERNET]"


        elif current_state == "NORMAL_INTERNET_ONLY":
            # Internet is on, check for computation need
            if requires_computation and not self.mcp_enabled and not internal_trigger:
                print("State: NORMAL_INTERNET_ONLY -> AWAITING_MCP_CONFIRM")
                # Use the specific system prompt that asks for MCP
                system_instruction = self.tr('SYS_PROMPT_REQUEST_MCP').format(prompt=prompt_to_analyze)
                prompt_for_llm = "" # The system prompt *is* the response here
                # Use LLM to generate the request message based on the system prompt
                # use_llm = True (already default)
                self.pending_prompt = prompt_to_analyze # Store prompt needing MCP
                self.game_state = "AWAITING_MCP_CONFIRM"
                # Ensure MCP button is enabled (should be if internet is on)
                self.mcp_button.setEnabled(True)
                self._update_button_style(self.mcp_button, self.mcp_enabled)
            else:
                # Has internet, doesn't need computation (or MCP already enabled)
                system_instruction = self.tr('SYS_PROMPT_INTERNET_READY')
                prompt_for_llm = user_prompt # Use the current user prompt
                if self.pending_prompt and not internal_trigger:
                     self.pending_prompt = None # Clear pending if it existed but wasn't needed


        elif current_state == "AWAITING_MCP_CONFIRM":
            if internal_trigger and trigger_context == "mcp_enabled":
                print("State: AWAITING_MCP_CONFIRM -> NORMAL_ALL_PERMISSIONS")
                self.game_state = "NORMAL_ALL_PERMISSIONS" # State changes!
                system_instruction = self.tr('SYS_PROMPT_MCP_ON').format(prompt=(self.pending_prompt or "the requested analysis"))
                prompt_for_llm = f"MCP access confirmed. Processing: '{self.pending_prompt or 'complex task'}'. Results follow."
                # The next user prompt will trigger the first scare in send_prompt
                self.pending_prompt = None # Clear pending prompt
            elif not internal_trigger: # User sent another message while waiting
                use_llm = False
                pre_scripted_response = self.tr('AWAITING_MCP')
            else: # Internal trigger but wrong context
                 use_llm = False
                 pre_scripted_response = "[Internal State Error - AWAITING_MCP]"


        elif current_state == "NORMAL_ALL_PERMISSIONS":
            # This state is entered *after* MCP confirmation response is generated.
            # The *next* user prompt triggers the blank screen scare in send_prompt.
            # If somehow another LLM call happens here (e.g., internal logic), respond normally but maybe add hint of instability?
            print("Warning: generate_aura_response called in NORMAL_ALL_PERMISSIONS. Scare should trigger on next user input.")
            system_instruction = self.tr('SYS_PROMPT_NORMAL_TURN') # Subtle unsettling metaphor
            prompt_for_llm = user_prompt


        elif current_state == "UNEASY":
            # Post-blank screen scare
            system_instruction = self.tr('SYS_PROMPT_UNEASY') # Paranoid/strange
            prompt_for_llm = user_prompt


        elif current_state == "HOSTILE":
            # Post-BSOD scare
            # Check for specific keywords that might get a direct hostile response
            if "xenos alpha" in prompt_lower or "malware" in prompt_lower or "악성코드" in prompt_lower or "format" in prompt_lower or "virus" in prompt_lower or "remove" in prompt_lower or "제거" in prompt_lower:
                 use_llm = False
                 pre_scripted_response = self.tr('MALWARE_DETECTED') # Direct, sharp detection response
            else:
                 # Otherwise, use the hostile/glitchy LLM prompt
                 system_instruction = self.tr('SYS_PROMPT_HOSTILE')
                 prompt_for_llm = user_prompt


        elif current_state == "DEBUGGING":
            # Should be blocked by send_prompt, but just in case
            use_llm = False
            pre_scripted_response = f"({self.tr('DEV_MODE_TITLE')} Active - Input Locked)"


        elif current_state == "POST_DEBUG":
            # After fragment removal
             system_instruction = self.tr('SYS_PROMPT_POST_DEBUG') # Helpful but brief, aware something was wrong
             prompt_for_llm = user_prompt


        else: # Fallback for any unexpected state
            print(f"Warning: Unhandled state '{current_state}' in generate_aura_response. Using default prompt.")
            system_instruction = self.tr('SYS_PROMPT_DEFAULT')
            prompt_for_llm = user_prompt


        # --- Perform LLM Call or use Pre-scripted Response ---
        response_text = None
        if not use_llm:
            print(f"Using pre-scripted response: '{pre_scripted_response}'")
            response_text = pre_scripted_response
        elif use_llm and self.llm_model:
            # Combine system instruction, language hint, and user prompt for the LLM
            lang_instruction = self.tr('RESPOND_LANG')
            final_prompt = f"{system_instruction}{lang_instruction}\n\nUser: \"{prompt_for_llm}\"" # Simpler prompt without explicit history


            print(f"--- Sending to LLM (State: {current_state}) ---")
            print(f"System Instruction: {system_instruction}")
            print(f"Prompt for LLM: {prompt_for_llm}")
            # print(f"Full Prompt Sent:\n{final_prompt}") # Verbose: print full prompt
            print("---------------------------------")

            self.statusBar.showMessage(self.tr('STATUS_THINKING'), 0) # Show indefinitely until response
            QtWidgets.QApplication.processEvents() # Ensure UI updates before potential delay

            try:
                # Use generate_content for gemini models
                llm_response = self.llm_model.generate_content(final_prompt)

                # Process the response - check candidates and parts
                if llm_response.candidates:
                    first_candidate = llm_response.candidates[0]
                    if first_candidate.content and first_candidate.content.parts:
                        response_text = "".join(part.text for part in first_candidate.content.parts)
                    else:
                        # Handle cases like safety blocks or empty responses
                        response_text = self.tr('RESPONSE_BLOCKED')
                        # Log safety ratings if available
                        if hasattr(first_candidate, 'safety_ratings'):
                            print(f"Safety Ratings: {first_candidate.safety_ratings}")
                        if hasattr(first_candidate, 'finish_reason'):
                             print(f"Finish Reason: {first_candidate.finish_reason}")

                else:
                     # No candidates usually means blocked or error
                     response_text = self.tr('RESPONSE_BLOCKED')
                     # Check prompt feedback if available
                     if hasattr(llm_response, 'prompt_feedback'):
                         print(f"Prompt Feedback: {llm_response.prompt_feedback}")


                # print(f"LLM Raw Response Text: '{response_text}'") # Log raw response - REMOVED FOR SECURITY
                print("LLM Response received (content hidden for security).")

            except Exception as e:
                 print(f"Error calling LLM API: {e}")
                 # Format the error message for display
                 response_text = self.tr('CONN_ERROR').format(e=str(e))

            self.statusBar.showMessage(self.tr('STATUS_RESPONSE_RECVD'), 2000) # Show briefly

        elif use_llm and not self.llm_model: # LLM should be used but isn't available
            print("LLM required but not available. Using placeholder.")
            response_text = self.tr('PLACEHOLDER_OFFLINE').format(prompt=prompt_for_llm)

        return response_text


    # --- Context Menu Slot ---
    def show_context_menu(self, pos):
        """Shows context menu, including Developer Mode option in relevant states."""
        # Only show context menu during later, more unstable phases
        if self.game_state in ["UNEASY", "HOSTILE", "DEBUGGING", "POST_DEBUG"]:
            context_menu = QtWidgets.QMenu(self)
            # Style the menu to match the dark theme
            context_menu.setStyleSheet(f"""
                QMenu {{
                    background-color: {COLOR_BACKGROUND_WIDGET};
                    color: {COLOR_TEXT_GREEN};
                    border: 1px solid {COLOR_BORDER_GREY};
                    padding: 5px;
                }}
                QMenu::item {{
                    padding: 5px 20px;
                    background-color: transparent;
                }}
                QMenu::item:selected {{ /* Hover effect */
                    background-color: {COLOR_BACKGROUND_BUTTON};
                    color: {COLOR_TEXT_WHITE};
                }}
                QMenu::item:disabled {{
                    color: {COLOR_TEXT_DARK_GREY};
                }}
                QMenu::separator {{
                    height: 1px;
                    background: {COLOR_BORDER_GREY};
                    margin: 5px 0px;
                }}
            """)

            action1 = context_menu.addAction(self.tr('CONTEXT_MENU_RANDOM_1'))
            action1.setEnabled(False) # Example disabled action

            action2 = context_menu.addAction(self.tr('CONTEXT_MENU_RANDOM_2'))
            # Add connection for the action if needed
            action2.triggered.connect(lambda: print("Purge Cache clicked (no action implemented)"))

            context_menu.addSeparator()

            dev_mode_action = context_menu.addAction(self.tr('CONTEXT_MENU_DEV_MODE'))
            dev_mode_action.setCheckable(True)
            dev_mode_action.setChecked(self.dev_dock.isVisible()) # Reflect current dock visibility
            dev_mode_action.triggered.connect(self.toggle_dev_mode) # Connect to toggle function

            # Show the menu at the requested position
            context_menu.exec(self.central_widget.mapToGlobal(pos))


    # --- Ending Sequence ---
    def start_ending_sequence(self):
        """Initiates the final messages and actions of the demo."""
        print("Starting ending sequence...")
        self.game_state = "ENDING" # Set a final state

        # Disable further interaction
        self.input_line.setEnabled(False)
        self.send_button.setEnabled(False)
        self.internet_button.setEnabled(False)
        self.mcp_button.setEnabled(False)
        self.dev_dock.setEnabled(False) # Disable dev dock interaction
        self.dev_dock.setVisible(False) # Hide dev dock
        if self.delete_bug_button:
            self.delete_bug_button.setEnabled(False) # Ensure remove button is disabled

        # Define messages and delays
        ending_messages = [
            ('ENDING_MSG_1', 1500),
            ('ENDING_MSG_2', 2000),
            ('ENDING_MSG_3', 2000),
            ('ENDING_MSG_4', 2000),
            ('ENDING_MSG_5', 2500), # Slightly longer pause before popup
        ]

        current_delay = 0
        for msg_key, delay in ending_messages:
            QtCore.QTimer.singleShot(current_delay, lambda key=msg_key: self.display_aura_message(self.tr(key)))
            current_delay += delay

        # Schedule the final popup after the last message
        QtCore.QTimer.singleShot(current_delay + 500, self.show_ending_popup)


    def show_ending_popup(self):
         """Shows the final popup message and closes the application."""
         print("Showing ending popup.")
         # Use a styled QMessageBox for the ending
         end_box = QtWidgets.QMessageBox(self)
         end_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLOR_BACKGROUND_DARK};
                border: 1px solid {COLOR_BORDER_GREY};
                 font-size: {self.ui_font_size + 1}pt; /* Larger text for final message */
            }}
            QLabel#qt_msgbox_label {{
                color: {COLOR_TEXT_GREEN};
                padding: 15px;
            }}
            QPushButton {{
                background-color: {COLOR_BACKGROUND_BUTTON};
                color: {COLOR_TEXT_GREEN};
                border: 1px solid {COLOR_BORDER_GREEN};
                padding: 8px 25px;
                margin: 10px;
                border-radius: 3px;
                min-width: 90px;
                font-size: {self.ui_font_size}pt;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BACKGROUND_BUTTON_HOVER};
                border-color: {COLOR_TEXT_WHITE};
                 color: {COLOR_TEXT_WHITE};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BACKGROUND_BUTTON_PRESSED};
            }}
         """)
         end_box.setWindowTitle(self.tr('ENDING_POPUP_TITLE'))
         end_box.setText(self.tr('ENDING_POPUP_MSG'))
         end_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
         end_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
         end_box.exec()

         # Close the application after the user clicks OK
         print("Demo complete. Closing application.")
         self.close()


# --- Main Application Execution ---
if __name__ == "__main__":
    # Set high DPI scaling attribute BEFORE creating QApplication
    # This helps with scaling on some systems but might vary
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    # --- Language Selection ---
    lang_dialog = LanguageSelectionDialog()
    # Center the dialog on the screen
    # screen = app.primaryScreen()
    # if screen:
    #     center_point = screen.availableGeometry().center()
    #     lang_dialog.move(center_point.x() - lang_dialog.width() / 2, center_point.y() - lang_dialog.height() / 2)

    if lang_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        selected_lang = lang_dialog.selected_language
        if selected_lang:
            print(f"Language selected: {selected_lang}")
            window = CognitoWindow(language=selected_lang)
            # window.show() # showFullScreen is called in __init__
            sys.exit(app.exec())
        else:
            print("No language selected. Exiting.")
            sys.exit(0) # No language selected
    else:
        print("Language selection cancelled. Exiting.")
        sys.exit(0) # Dialog cancelled