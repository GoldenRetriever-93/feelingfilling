package com.a702.feelingfilling.domain.history.controller;

import com.a702.feelingfilling.domain.history.model.dto.*;
import com.a702.feelingfilling.domain.history.service.StatService;
import com.a702.feelingfilling.domain.user.model.dto.UserLoginDTO;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@CrossOrigin(origins = {"*"}, maxAge = 6000)
@RestController
@RequestMapping("/api/stat")
@Api(tags = {"통계 API"})
@Slf4j
public class StatController {
	
	public static final Logger logger = LoggerFactory.getLogger(StatController.class);
	private static final String SUCCESS = "success";
	private static final String FAIL = "fail";
	private static final String ALREADY_EXIST = "already exists";
	private static final int burger = 6500;
	private static final int coffee = 4500;
	
	@Autowired
	private StatService statService;
	
		
	@ApiOperation(value = "유저 통계", notes = "유저 통계 API", response = Map.class)
	@GetMapping("/user")
	public ResponseEntity<?> getUserStat(){
		HttpStatus status = HttpStatus.OK;
		Map<String, Object> resultMap = new HashMap<>();
		
		try{
			int userId = ((UserLoginDTO) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getId();
			//이번 달 저금
			UserStat[] stats = statService.getUserThisMonth(userId);
			resultMap.put("userThisMonth",stats);
			logger.debug("사용자 이번 달 저금 : ", stats);
			
			//월별 추이
//			List<Month> months = requestService.getUserMonths(userId);
			Month[][] months = statService.getUserMonths(userId);
			resultMap.put("userMonths",months);
			logger.debug("사용자 월별 추이", months);
			
			//이번 달 감정 최고조
			EmotionHigh emotionHigh = statService.getEmotionHigh(userId);
			resultMap.put("emotionHigh",emotionHigh);
			logger.debug("사용자 이번 달 감정 최고 : ", emotionHigh);
			
			//저금 누적액
			int userTotal = statService.getUserTotal(userId);
			resultMap.put("total",userTotal);
			resultMap.put("coffee", userTotal/coffee);
			resultMap.put("burger",userTotal/burger);
			logger.debug("사용자 적금 누적액 : ", userTotal);
			logger.debug("사용자 적금 누적액/커피값 : ", userTotal/coffee);
			logger.debug("사용자 적금 누적액/버거값 : ", userTotal/burger);
			
			resultMap.put("message", SUCCESS);
			
		}
		catch (Exception e){
			status = HttpStatus.BAD_REQUEST;
			resultMap.put("message", FAIL);
			logger.error("유저 통계 에러 : {} ",e);
		}
		
		return new ResponseEntity<>(resultMap,status);
	}
		
	@ApiOperation(value = "전체 통계", notes = "전체 통계 API", response = Map.class)
	@GetMapping("/all")
	public ResponseEntity<?> getTotalStat(){
		HttpStatus status = HttpStatus.OK;
		Map<String, Object> resultMap = new HashMap<>();
		
		try{
			//이번 달 저금
			Stat[] stats = statService.getThisMonth();
			resultMap.put("totalThisMonth", stats);
			logger.debug("전체 사용자 이번 달 저금 : ", stats);
			
			//전날 추이
			Yesterday[][] yesterday = statService.getYesterday();
			resultMap.put("yesterday",yesterday);
			logger.debug("전날 추이 : ", yesterday);
			
			//이번 달 감정왕
			EmotionKing emotionKing = statService.getEmotionKing();
			resultMap.put("emotionKing", emotionKing);
			logger.debug("이번 달 감정왕 : ", emotionKing);
			
			//전체 사용자 누적 적금액
			Stat[] total = statService.getTotal();
			resultMap.put("total", total);
			logger.debug("전체 사용자 누적 적금액 : ", total);
			
			resultMap.put("message", SUCCESS);
			
		}
		catch (Exception e){
			status = HttpStatus.BAD_REQUEST;
			resultMap.put("message", FAIL);
			logger.error("전체 사용자 통계 에러 : {} ",e);
		}
		
		return new ResponseEntity<>(resultMap,status);
	}
}