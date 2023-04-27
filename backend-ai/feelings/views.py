import json
import requests
import time
import datetime
import logging
import jwt

from ..FEELINGFILLING_DJANGO import settings
from pymongo import MongoClient
from time import sleep
from transformers import pipeline
from googletrans import Translator
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from apscheduler.schedulers.background import BackgroundScheduler
from .models import React, Chatting, Request, User

jwt_token = ""


# 텍스트 번역 api
# post 요청
@api_view(['POST'])
def analysis_text(request):
    # 받아온 text 데이터
    start = time.time()
    # 토큰 decode해서 userid 추출
    # token = request.headers.get('Authorization').split(' ')[1]
    # user_id = decode_jwt_token(token)
    # if not user_id:
    #         # jwt 검증 실패시 예외 처리
    #         return HttpResponse(status=401, content='Authentication failed')
    
    text = request.data['TEXT']
    
    """
        chatting 저장
    """
    user = User.objects.get(user_id = 1)
    user = User.objects.get(user_id = user_id)
    result = insert_chatting(text)
    print(result)

    """
        번역 요청
    """
    feeling, score, trans = translation_text(text)

    """
        적금 금액 계산
    """
    amount = cal_deposit(score)

    """
        react 데이터 저장 (GPT 답변)
        일단 주석
    """
    # react = React(chatting = chatting, content = "GPT 답변!", emotion = feeling, amount = amount)
    # react.save()

    """
        billing 요청
        0 // 1
    """
    success = req_billing(amount, 1)
    # success = req_billing(token, amount, user_id)
    if success:
        # request 데이터 저장 (success 받아와야 함)
        request = Request(user = user, content = text, request_time = datetime.datetime.now(),
                        translation = trans, react = "GPT 답변", emotion = feeling, intensity = score,
                        amount = amount, success = 1)
        request.save()
        context = {
            "react" : "GPT 답변",
            "emotion" : feeling,
            "amount" : amount,
            "success" : success
        }
    else :
        context = {
            "react" : 0,
            "emotion" : 0,
            "amount" : 0,
            "success" : success
        }

    end = time.time()
    due_time = str(datetime.timedelta(seconds=(end-start))).split(".")
    print(f"소요시간 : {due_time}")
    return JsonResponse(context, status = 201)


# 음성 번역 api
# post 요청
@api_view(['POST'])
def analysis_voice(request):
    start = time.time()
    # 토큰 decode해서 userid 추출
    token = request.headers.get('Authorization').split(' ')[1]
    user_id = decode_jwt_token(token)
    if not user_id:
            # jwt 검증 실패시 예외 처리
            return HttpResponse(status=401, content='Authentication failed')
    
    """
        STT 요청
    """
    try:
        # 파일 받기
        voice = request.FILES.get('file')
        if voice is not None:
            config = {
                "diarization": {
                    "use_verification": False
                },
                "use_multi_channel": False
            }
            # 파일 TTS 요청
            resp = requests.post(
                'https://openapi.vito.ai/v1/transcribe',
                headers={'Authorization': 'bearer ' + jwt_token},
                data={'config': json.dumps(config)},
                files={'file': (voice.name, voice.read())},
            )
            resp.raise_for_status()
            id = resp.json()['id']
            # TTS 결과값 받기
            while True:
                resp = requests.get(
                    'https://openapi.vito.ai/v1/transcribe/'+id,
                    headers={'Authorization': 'bearer '+jwt_token},
                )
                resp.raise_for_status()
                if resp.json()['status'] == "completed":
                    # 응답이 성공적으로 온 경우
                    break
                else:
                    # 응답이 오지 않은 경우 1촣 재요청
                    print(f'Retrying after 1 seconds...')
                    sleep(1)
            print(resp.json())
            
        else : print("파일 없음!")
    except Exception as e:
        print(e)
    text = resp.json()

    """
        chatting 저장
    """
    user = User.objects.get(user_id = user_id)
    result = insert_chatting(text)
    print(result)

    """
        번역 요청
    """
    feeling, score, trans = translation_text(resp.json())

    """
        적금 금액 계산
    """
    amount = cal_deposit(score)
    
    """
        react 데이터 저장 (GPT 답변)
    """
    # react = React(chatting = chatting, content = "GPT 답변!", emotion = feeling, amount = amount)
    # react.save()
    # chatting에 react도 저장해야함??
    """
        billing 요청
    """
    success = req_billing(token, amount, user_id)

    # 성공한 경우
    if (success) :
        # request 데이터 저장 (success 받아와야 함)
        request = Request(user = user, content = resp.json(), request_time = datetime.datetime.now(),
                        translation = trans, react = "GPT 답변", emotion = feeling, intensity = score,
                        amount = amount, success = success)
        request.save()
        context = {
            "react" : "GPT 답변",
            "emotion" : feeling,
            "amount" : amount,
            "success" : success
        }
    # 실패한 경우
    else :
        request = Request(user = user, content = resp.json(), request_time = datetime.datetime.now(),
                translation = trans, react = "GPT 답변", emotion = "", intensity = 0,
                amount = 0, success = success)
        request.save()
        context = {
            "react" : 0,
            "emotion" : 0,
            "amount" : 0,
            "success" : success
        }


    end = time.time()
    due_time = str(datetime.timedelta(seconds=(end-start))).split(".")
    print(f"소요시간 : {due_time}")
    return JsonResponse(context, status = 201)


# 측정된 감정 정도에 따라 적금 금액 계산
def cal_deposit(score):
    user= User.objects.get(user_id = 1)
    min, max = user.minimum, user.maximum
    amount = round((max - min + 1) * (score-0.333333))
    print(amount)
    return amount


# GPT // ChatBot react 생성 함수
def make_react():
    pass


# chatting에 insert 함수
def insert_chatting(text):
    # MongoDB 클라이언트 생성
    client = MongoClient('mongodb://3.38.191.128:27017/')
    # 데이터베이스 선택
    db = client['feelingfilling']
    # 컬렉션 선택
    collection = db['chatting']
    # 문서 생성
    chat = {"user": 1, "text": text, "date": datetime.datetime.now()}
    # 문서 삽입
    result = collection.insert_one(chat)
    # # 단일 문서 조회
    # post = posts.find_one({"author": "Mike"})
    # # 다중 문서 조회
    # for post in posts.find():
    #     print(post)
    return result


# 번역 함수
def translation_text(text):
    google = Translator()
    text = text

    abs_translator = google.translate(text, dest="en")

    print("----------------------------------------------------------------")
    print("TRANSLATION")
    print(f"""{text}
    *****************************************************************
    {abs_translator.text}""")
    print("----------------------------------------------------------------")

    return analysis_emition(abs_translator)


# 감정 분석 함수
def analysis_emition(translation_result): 
    # 번역
    classifier = pipeline("text-classification",
                          model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=True)
    prediction = classifier(translation_result.text)
    print("----------------------------------------------------------------")
    print("TOTAL PREDICTIONS")
    print(prediction)
    print("----------------------------------------------------------------")

    # 최대 감정과 감정 스코어 출력
    max_feeling = ''
    max_score = 0

    scores = [0, 0, 0]
    feelings = ["joy", "sadness", "anger"]

    for p in prediction[0]:
        score = p['score']
        feeling = p['label']
        
        # 각 감정을 서비스 기준에 맞게 재집계
        if (feeling == "love" or feeling == "joy") : scores[0] += score
        elif (feeling == "sadness") : scores[1] += score
        elif (feeling == "anger") : scores[2] += score
        elif (feeling == "fear") :
            scores[1] += score * 0.35
            scores[2] += score * 0.65
        elif (feeling == "surprise") :
            scores[1] += score * 0.5
            scores[2] += score * 0.5

    # max 감정과 스코어 추출
    max_score = max(scores)
    max_feeling = feelings[scores.index(max(scores))]

    print("----------------------------------------------------------------")
    print("MAX EMOTION")
    print(max_feeling, max_score)
    print("----------------------------------------------------------------")
    return max_feeling, max_score, translation_result.text


# Billing에 요청 함수
def req_billing(token, amount, user_id):
    headers = { 'Authorization' : 'Bearer' + token}
    resp = requests.post(
        'http://3.38.191.128:8080/billing/subscription',
        headers=headers,
        data={
            'serviceUserId': user_id,
            'serviceName': "FeelingFilling",
            'amount': amount
        }
    )
    success = 1
    return success


# jwt decode 함수
def decode_jwt_token(access_token):
    try:
        decoded_token = jwt.decode(access_token, settings.JWT_SECRET, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')
        return user_id
    except jwt.ExpiredSignatureError:
        # 토큰이 만료되었을 때 예외 처리
        return HttpResponse(status=401, content='Expired token')
    except jwt.InvalidTokenError:
        # 토큰이 올바르지 않을 때 예외 처리
        return HttpResponse(status=401, content='Invalid token')


# 초기에 모델을 받는데 시간이 오래걸림 // 초기 세팅 함수
def init_setting():
    get_jwt()
    classifier = pipeline("text-classification",
                          model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=True)
    classifier("")


"""
    STT JWT TOKEN
    인증 요청
    token의 만료 기간은 6시간
    주기적으로 token이 갱신될 수 있도록 /v1/authenticate 을 통해 token을 갱신해야 합니다.
    갱신은 스케줄링을 통해 작성
    client_id / client_secret 환경변수로 빼거나 따로 작성!!
"""


def get_jwt():
    global jwt_token
    print("start schd")
    resp = requests.post(
        'https://openapi.vito.ai/v1/authenticate',
        data={'client_id': "cnmeuourK_cZS7UMpGwG",
              'client_secret': "8XHGuP-vT3HJNK0R9zfxeK97eciLUcHF5jPKyhsz"}
    )
    resp.raise_for_status()
    jwt_token = resp.json()['access_token']
    print(resp.json()['access_token'])


def schedule_api():
    print("starting update JWT")
    sched = BackgroundScheduler()
    sched.add_job(get_jwt, 'interval', hours=5, minutes=30)
    try:
        sched.start()
    except Exception as e:
        logging.exception(f"Error in background job: {str(e)}")


# 맨 처음 실행
init_setting()

# 스케줄러 api 실행
schedule_api()