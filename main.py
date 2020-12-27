import win32com.client
import pythoncom
import config
import time
import threading
import datetime


class Requests:
    session = None
    tr_obj = None
    cspat_obj = None
    k3_obj = None
    ha_obj = None
    SC0_obj = None
    SC1_obj = None

    @staticmethod
    def init():
        Requests.session = win32com.client.DispatchWithEvents("XA_Session.XASession", XS_event_handler)
        Requests.tr_obj = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XQ_event_handler)
        Requests.k3_obj = win32com.client.DispatchWithEvents("XA_DataSet.XAReal", XR_event_handler)
        Requests.ha_obj = win32com.client.DispatchWithEvents("XA_DataSet.XAReal", XR_event_handler)
        Requests.cspat_obj = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XQ_event_handler)
        Requests.SC0_obj = win32com.client.DispatchWithEvents("XA_DataSet.XAReal", XR_event_handler)
        Requests.SC1_obj = win32com.client.DispatchWithEvents("XA_DataSet.XAReal", XR_event_handler)
        Requests.login()

    @staticmethod
    def login():
        Requests.session.ConnectServer(config.server + ".ebestsec.co.kr", 20001)
        Requests.session.Login(config.id, config.password, config.cert_password, 0, False)

        while Responses.login_status is False:
            pythoncom.PumpWaitingMessages()

    # 종목코드 리스트 받아오기
    @staticmethod
    def t8436(gubun):
        Requests.tr_obj.ResFileName = "C:/eBEST/xingAPI/Res/t8436.res"
        Requests.tr_obj.SetFieldData("t8436InBlock", "gubun", 0, gubun)
        Requests.tr_obj.Request(False)

        Responses.tr_ok = False
        while Responses.tr_ok is False:
            pythoncom.PumpWaitingMessages()

    # 해당종목 가격 조회
    @staticmethod
    def t8412(shcode, ncnt=1, qrycnt=500, nday="0", sdate="", edate="당일", cts_date="", cts_time="", comp_yn="N", _next=False):
        time.sleep(1.1)

        Requests.tr_obj.ResFileName = "C:/eBEST/xingAPI/Res/t8412.res"

        Requests.tr_obj.SetFieldData("t8412InBlock", "shcode", 0, shcode)
        Requests.tr_obj.SetFieldData("t8412InBlock", "ncnt", 0, ncnt)
        Requests.tr_obj.SetFieldData("t8412InBlock", "qrycnt", 0, qrycnt)
        Requests.tr_obj.SetFieldData("t8412InBlock", "nday", 0, nday)
        Requests.tr_obj.SetFieldData("t8412InBlock", "sdate", 0, sdate)
        Requests.tr_obj.SetFieldData("t8412InBlock", "edate", 0, edate)
        Requests.tr_obj.SetFieldData("t8412InBlock", "cts_date", 0, cts_date)
        Requests.tr_obj.SetFieldData("t8412InBlock", "cts_time", 0, cts_time)
        Requests.tr_obj.SetFieldData("t8412InBlock", "comp_yn", 0, comp_yn)

        Requests.tr_obj.Request(_next)

        Responses.tr_ok = False
        while Responses.tr_ok is False:
            pythoncom.PumpWaitingMessages()

    # 잔고 조회
    @staticmethod
    def t0424(cts_expcode="", _next=False):
        Requests.tr_obj.ResFileName = "C:/eBEST/xingAPI/Res/t0424.res"
        Requests.tr_obj.SetFieldData("t0424InBlock", "accno", 0, config.account_num)
        Requests.tr_obj.SetFieldData("t0424InBlock", "passwd", 0, config.account_password)
        Requests.tr_obj.SetFieldData("t0424InBlock", "prcgb", 0, "1")
        Requests.tr_obj.SetFieldData("t0424InBlock", "chegb", 0, "2")
        Requests.tr_obj.SetFieldData("t0424InBlock", "dangb", 0, "0")
        Requests.tr_obj.SetFieldData("t0424InBlock", "charge", 0, "1")
        Requests.tr_obj.SetFieldData("t0424InBlock", "cts_expcode", 0, cts_expcode)

        Requests.tr_obj.Request(_next)

        Responses.tr_ok = False
        while Responses.tr_ok is False:
            pythoncom.PumpWaitingMessages()


    # 실시간 해당종목 체결정보
    @staticmethod
    def K3_(shcode):
        Requests.k3_obj.ResFileName = "C:/eBEST/xingAPI/Res/K3_.res"
        Requests.k3_obj.SetFieldData("InBlock", "shcode", shcode)
        Requests.k3_obj.AdviseRealData()

    # 실시간 해당종목 호가잔량
    @staticmethod
    def HA_(shcode):
        Requests.ha_obj.ResFileName = "C:/eBEST/xingAPI/Res/HA_.res"
        Requests.ha_obj.SetFieldData("InBlock", "shcode", shcode)
        Requests.ha_obj.AdviseRealData()

    # 주문
    @staticmethod
    def CSPAT00600(IsuNo, OrdQty, BnsTpCode):
        Requests.cspat_obj.ResFileName = "C:/eBEST/xingAPI/Res/CSPAT00600.res"
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "AcntNo", 0, config.account_num)
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "InptPwd", 0, config.account_password)

        if config.server == "demo":
            IsuNo = "A" + IsuNo

        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "IsuNo", 0, IsuNo) # 종목번호
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "OrdQty", 0, OrdQty) # 주문량
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "OrdPrc", 0, 0) # 주문가
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "BnsTpCode", 0, BnsTpCode) # "1":매도, "2":매수
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "OrdprcPtnCode", 0, "03") # 호가유형코드, "03":시장가
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "MgntrnCode", 0, "000") # 신용거래코드, "000":보통
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "LoanDt", 0, "") # 대출일
        Requests.cspat_obj.SetFieldData("CSPAT00600InBlock1", "OrdCndiTpCode", 0, "0") # 주문조건구분, "0":없음, "1":IOC, "2":FOK

        err = Requests.cspat_obj.Request(False)

        if err < 0:
            print()
            print("XXXXXXXXXXXXXXXXXXXXX")
            print("CSPAT00600 주문에러")
            print(f"계좌번호: {config.account_num}")
            print(f"종목코드: {IsuNo}")
            print(f"주문수량: {OrdQty}")
            print(f"매매구분: {BnsTpCode}")
            print(f"주문에러: {err}")
            print()
        else:
            print()
            print("======================")
            print("CSPAT00600 주문 실행")
            print(f"계좌번호: {config.account_num}")
            print(f"종목코드: {IsuNo}")
            print(f"주문수량: {OrdQty}")
            print(f"매매구분: {BnsTpCode}")
            print()

    @staticmethod
    def SC0():
        Requests.SC0_obj.ResFileName = "C:/eBEST/xingAPI/Res/SC0.res"
        Requests.SC0_obj.AdviseRealData()

    @staticmethod
    def SC1():
        Requests.SC1_obj.ResFileName = "C:/eBEST/xingAPI/Res/SC1.res"
        Requests.SC1_obj.AdviseRealData()

    @staticmethod
    def t1857():
        Requests.tr_obj.ResFileName = "C:/eBEST/xingAPI/Res/t1857.res"
        Requests.tr_obj.SetFieldData("t1857InBlock", "sRealFlag", 0, "0")
        Requests.tr_obj.SetFieldData("t1857InBlock", "sSearchFlag", 0, "F")
        Requests.tr_obj.SetFieldData("t1857InBlock", "query_index", 0, "files/ConditionToApi.ACF")

        Requests.tr_obj.RequestService("t1857", "")
        # Requests.tr_obj.Request(False)

        Responses.tr_ok = False
        while Responses.tr_ok is False:
            pythoncom.PumpWaitingMessages()




class Responses:
    login_status = False
    tr_ok = False
    real_ok = False
    balanceUpdating = True
    MAX_NUM = 20
    MAX_PRICE = 3000
    have_num = 0

    k3_dict = {} # 실시간 주식 정보
    ha_dict = {} # 실시간 호가 정보
    t8436_list = [] # 주식코드 리스트
    t0424_dict = {} # 잔고내역
    # sum_n_dict = {} # 종목 최근 n일 종가 합계
    min_dict = {} # 분봉 {"종목코드": [[시간, 시가, 고가, 저가, 종가], [시간, 시가, 고가, 저가, 종가], ...]}
    t1857_list = [] # 조건검색 결과 종목코드

    @staticmethod
    def login(szCode, szMsg):
        print(f"login: {szCode} {szMsg}")
        if szCode == "0000":
            Responses.login_status = True
        else:
            Responses.login_status = False

    @staticmethod
    def t8436(obj):
        occurs_count = obj.GetBlockCount("t8436OutBlock")
        print(f"종목 갯수: {occurs_count}")
        for i in range(occurs_count):
            shcode = obj.GetFieldData("t8436OutBlock", "shcode", i)
            Responses.t8436_list.append(shcode)

        print(f"종목 리스트: {Responses.t8436_list}")
        Responses.tr_ok = True

    @staticmethod
    def t8412(obj):
        shcode = obj.GetFieldData("t8412OutBlock", "shcode", 0)
        cts_date = obj.GetFieldData("t8412OutBlock", "cts_date", 0)
        cts_time = obj.GetFieldData("t8412OutBlock", "cts_time", 0)

        occurs_count = obj.GetBlockCount("t8412OutBlock1")
        sum_close = 0
        for i in range(occurs_count-1):
            date = obj.GetFieldData("t8412OutBlock1", "date", i)
            time = obj.GetFieldData("t8412OutBlock1", "time", i)
            close = float(obj.GetFieldData("t8412OutBlock1", "close", i))
            sum_close += close
            print(f"date: {date}, time: {time}, close: {close}")

        # Responses.sum_n_dict[shcode + "_" + str(occurs_count)] = sum_close

        Responses.tr_ok = True
        # if obj.IsNext is True:
        #     print(f"연속조회 기준 날짜: {cts_date}")
        #     Requests.t8412(shcode, cts_date, cts_time, _next=True)
        # else:
        #     Responses.tr_ok = True

    @staticmethod
    def t0424(obj):
        if not Responses.balanceUpdating:
            Responses.t0424_dict.clear()
            Responses.balanceUpdating = True

        Responses.have_num = 0

        cts_expcode = obj.GetFieldData("t0424OutBlock", "cts_expcode", 0)

        occurs_count =  obj.GetBlockCount("t0424OutBlock1")
        for i in range(occurs_count):
            expcode = obj.GetFieldData("t0424OutBlock1", "expcode", i)

            Responses.t0424_dict[expcode] = {}

            table = Responses.t0424_dict[expcode]
            table["잔고수량"] = int(obj.GetFieldData("t0424OutBlock1", "janqty", i))
            table["매도가능수량"] = int(obj.GetFieldData("t0424OutBlock1", "mdposqt", i))
            table["평균단가"] = int(obj.GetFieldData("t0424OutBlock1", "pamt", i))
            table["종목명"] = obj.GetFieldData("t0424OutBlock1", "hname", i)
            table["종목구분"] = obj.GetFieldData("t0424OutBlock1", "jonggb", i)
            table["수익률"] = float(obj.GetFieldData("t0424OutBlock1", "sunikrt", i))

            Responses.have_num += table["잔고수량"]


        if obj.IsNext is True:
            Requests.t0424(cts_expcode, True)
        else:
            Responses.tr_ok = True
            Responses.balanceUpdating = False

            print(f"잔고내역: {Responses.t0424_dict}")

            # 매도
            for shcode in Responses.t0424_dict:
                balance = Responses.t0424_dict[shcode]
                if balance["매도가능수량"] > 0 and (balance["수익률"] > 1 or balance["수익률"] < -1):
                    balance["매도가능수량"] -= balance["잔고수량"]
                    Requests.CSPAT00600(IsuNo=shcode, OrdQty=balance["잔고수량"], BnsTpCode="1")


    @staticmethod
    def K3_(obj):
        shcode = obj.GetFieldData("OutBlock", "shcode")

        if shcode not in Responses.k3_dict:
            Responses.k3_dict[shcode] = {}

        table = Responses.k3_dict[shcode]
        table["체결시간"] = obj.GetFieldData("OutBlock", "chetime")
        table["등락율"] = float(obj.GetFieldData("OutBlock", "drate"))
        table["현재가"] = int(obj.GetFieldData("OutBlock", "price"))
        table["시가"] = int(obj.GetFieldData("OutBlock", "open"))
        table["고가"] = int(obj.GetFieldData("OutBlock", "high"))
        table["저가"] = int(obj.GetFieldData("OutBlock", "low"))
        table["누적거래량"] = int(obj.GetFieldData("OutBlock", "volume"))
        table["매도호가"] = int(obj.GetFieldData("OutBlock", "offerho"))
        table["매수호가"] = int(obj.GetFieldData("OutBlock", "bidho"))

        # # t8412 분봉데이터를 이용한 이동평균 계산
        # sum_9_key = shcode + "_9"
        # avg_10_price = 0
        # if sum_9_key in Responses.sum_n_dict:
        #     avg_10_price = (Responses.sum_n_dict[sum_9_key] + table["현재가"]) / 10
        #     print(f"{shcode}의 10이동평균: {avg_10_price}")
        # table["10이동평균선"] = avg_10_price

        ## 실시간 분봉데이터 생성
        chetime = table["체결시간"]
        price = table["현재가"]
        open = table["시가"]

        if shcode not in Responses.min_dict:
            Responses.min_dict[shcode] = [] # {"종목코드": [[시간, 시가, 고가, 저가, 종가], ...]}
            min_list = [chetime, price, price, price, price]
            Responses.min_dict[shcode].append(min_list)

        last_time = Responses.min_dict[shcode][-1][0]
        last_t = datetime.datetime.strptime(last_time[0:4], "%H%M").time()
        last_hour, last_min = last_t.hour, last_t.minute
        last_min = last_min + 60*last_hour

        current_t = datetime.datetime.strptime(chetime[0:4], "%H%M").time()
        current_hour, current_min = current_t.hour, current_t.minute
        current_min = current_min + 60*current_hour

        diff_min = current_min - last_min

        # 새로운 분봉 생성
        if diff_min >= 0:
            add_min = datetime.timedelta(minutes=1)

            last_time = Responses.min_dict[shcode][-1][0]
            chk_t = datetime.datetime.strptime(last_time[0:4], "%H%M")
            last_price = Responses.min_dict[shcode][-1][4]
            next_min = chk_t + add_min

            # 2분 이상 체결되지 않았을 때: 분봉은 실선이므로 기존 종가를 넣어준다.
            for i in range(diff_min):
                next_min_str = next_min.strftime("%H%M00")
                min_list = [next_min_str, last_price, last_price, last_price, last_price]
                Responses.min_dict[shcode].append(min_list)
                next_min = next_min + add_min

            # 현재 종가
            next_min_str = next_min.strftime("%H%M00")
            min_list = [next_min_str, price, price, price, price]
            Responses.min_dict[shcode].append(min_list)
        # 기존 분봉 업데이트
        else:
            last_high = Responses.min_dict[shcode][-1][2]
            last_low = Responses.min_dict[shcode][-1][3]

            Responses.min_dict[shcode][-1][4] = price # 종가 업데이트
            if price > last_high:
                Responses.min_dict[shcode][-1][2] = price # 고가 업데이트
            elif price < last_low:
                Responses.min_dict[shcode][-1][3] = price # 저가 업데이트

        # print(f"{shcode} 분봉: {Responses.min_dict[shcode]}")

        # 이동평균선 만들기
        if len(Responses.min_dict[shcode]) >= 11:
            sample_10 = Responses.min_dict[shcode][-10:]
            sum_price = 0
            for sample_list in sample_10:
                sum_price += sample_list[4]
            table["10이동평균선"] = sum_price / 10
            # print(f"{shcode} 10이동평균선: {table['10이동평균선']}")
        else:
            return

        # 매수
        if shcode in Responses.ha_dict and Responses.ha_dict[shcode]["매수호가잔량4"] > 0 and \
                Responses.ha_dict[shcode]["매도호가잔량4"] > 0:

            # 매수(골든크로스 돌파시에만)
            if table["현재가"] < Responses.MAX_PRICE and not Responses.balanceUpdating and Responses.have_num < Responses.MAX_NUM\
                    and "10이동평균선" in table and Responses.min_dict[shcode][-2][4] < table["10이동평균선"] < table["현재가"]\
                    and (shcode not in Responses.t0424_dict or Responses.t0424_dict[shcode]["잔고수량"] < 5):
                Requests.CSPAT00600(IsuNo=shcode, OrdQty=1, BnsTpCode="2")
                Responses.have_num += 1

    @staticmethod
    def HA_(obj):
        shcode = obj.GetFieldData("OutBlock", "shcode")

        if shcode not in Responses.ha_dict:
            Responses.ha_dict[shcode] = {}

        table = Responses.ha_dict[shcode]
        table["매수호가잔량4"] = int(obj.GetFieldData("OutBlock", "bidrem4"))
        table["매도호가잔량4"] = int(obj.GetFieldData("OutBlock", "offerrem4"))

    @staticmethod
    def SC0(obj):
        ordno = obj.GetFieldData("OutBlock", "ordno")   # 주문번호
        ordqty = obj.GetFieldData("OutBlock", "ordqty") # 주문수량
        ordgb = obj.GetFieldData("OutBlock", "ordgb")   # 주문구분
        shtcode = obj.GetFieldData("OutBlock", "shtcode")   # 종목코드 7자리

        print(f"주문접수 SC0 - 주문번호: {ordno}, 주문수량: {ordqty}, 주문구분: {ordgb}, 종목코드: {shtcode}")

    @staticmethod
    def SC1(obj):
        ordno = obj.GetFieldData("OutBlock", "ordno")  # 주문번호
        execqty = obj.GetFieldData("OutBlock", "execqty")  # 체결수량
        execgb = obj.GetFieldData("OutBlock", "execgb")  # 체결구분
        shtcode = obj.GetFieldData("OutBlock", "shtcode")  # 종목코드 7자리

        print(f"주문접수 SC1 - 주문번호: {ordno}, 체결수량: {execqty}, 체결구분: {execgb}, 종목코드: {shtcode}")

    @staticmethod
    def t1857(obj):
        result_count = obj.GetFieldData("t1857OutBlock", "result_count", 0)
        result_time = obj.GetFieldData("t1857OutBlock", "result_time", 0)

        Responses.t1857_list.clear()

        occurs_count = obj.GetBlockCount("t1857OutBlock1")
        for i in range(occurs_count):
            shcode = obj.GetFieldData("t1857OutBlock1", "shcode", i)
            hname = obj.GetFieldData("t1857OutBlock1", "hname", i) # 종목이름

            Responses.t1857_list.append(shcode)

        Responses.tr_ok = True

# 실시간 수신 데이터
class XR_event_handler:
    def OnReceiveRealData(self, code):
        if code == "K3_":
            Responses.K3_(self)
        elif code == "HA_":
            Responses.HA_(self)
        elif code == "SC0":
            Responses.SC0(self)
        elif code == "SC1":
            Responses.SC1(self)

# TR 요청 수신 데이터
class XQ_event_handler:
    def OnReceiveData(self, code):
        if code == "t8436":
            Responses.t8436(self)
        elif code == "t8412":
            Responses.t8412(self)
        elif code == "t0424":
            Responses.t0424(self)
        elif code == "t1857":
            Responses.t1857(self)

    def OnReceiveMessage(self, systemError, messageCode, message):
        if messageCode != "00000":
            print(f"systemError: {systemError}, messageCode: {messageCode}, messaage: {message}")


# 서버접속, 로그인 수신 데이터
class XS_event_handler:
    def OnLogin(self, szCode, szMsg):
        Responses.login(szCode, szMsg)


if __name__ == '__main__':
    Requests.init()
    # Requests.t8436(gubun="2")
    # Requests.t8412(shcode="000250", qrycnt=10)
    Requests.K3_("018000")
    Requests.t1857()
    print(f"조건검색 결과: {Responses.t1857_list}")
    for shcode in Responses.t1857_list:
        Requests.K3_(shcode)
        Requests.HA_(shcode)

    def t0424_loop():
        Requests.t0424()
        threading.Timer(10, t0424_loop).start()
    t0424_loop()

    Requests.SC0()
    Requests.SC1()

    while True:
        pythoncom.PumpWaitingMessages()