package com.a702.feelingfilling.domain.user.service;

import com.a702.feelingfilling.domain.user.model.dto.UserDTO;
import com.a702.feelingfilling.domain.user.model.dto.UserLoginDTO;
import com.a702.feelingfilling.domain.user.model.dto.UserJoinDTO;
import com.a702.feelingfilling.domain.user.model.entity.User;
import com.a702.feelingfilling.domain.user.model.entity.UserBadge;
import com.a702.feelingfilling.domain.user.model.repository.UserBadgeRepository;
import com.a702.feelingfilling.domain.user.model.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class UserServiceImpl implements UserService{
	@Autowired
	UserBadgeRepository userBadgeRepository;
	@Autowired
	UserRepository userRepository;
	
	private int badgeCnt = 15;
	
	@Override
	public void join(UserJoinDTO userJoinDTO){
		User userEntity = userRepository.findByUserId(userJoinDTO.getUserId());
		if(userEntity == null) throw new IllegalArgumentException("KAKAO ID is not connected");
		int max = userJoinDTO.getMaximum();
		int min = userJoinDTO.getMinimum();
		if(min<0) throw new IllegalArgumentException("Unvalid Minimum Value");
		if(max<min) throw new IllegalArgumentException("Unvalid Maximum Value");
		userEntity.updateRange(userJoinDTO.getMaximum(), userJoinDTO.getMinimum());
		userEntity.updateJoinDate();
		userEntity.updateRole("ROLE_USER");
		userRepository.save(userEntity);
	}

	@Override
	public int getLoginUserId(){
		UserLoginDTO loginUser = (UserLoginDTO) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
		return loginUser.getId();
	}

//	public UserDTO getUser(){
//		UserLoginDTO loginUser = (UserLoginDTO) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
//		User userEntity = userRepository.findByUserId(loginUser.getId());
	public UserDTO getUser(int userId){
		User userEntity = userRepository.findByUserId(userId);
		
		return UserDTO.toDTO(userEntity);
	}
	
	
	@Override
	public UserDTO modifyUser(UserDTO userDTO) {
		//int userId = ((UserLoginDTO) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getId();
		
		User user = userRepository.findByUserId(userDTO.getUserId());
		
		user.setMaximum(userDTO.getMaximum());
		user.setMinimum(userDTO.getMinimum());
		user.setNickname(userDTO.getNickname());
		
		return UserDTO.toDTO(userRepository.save(user));
	}
	
	@Override
	public List<Integer> getUserBadge(int userId) {
//	public List<Integer> getUserBadge() {
		//int userId = ((UserLoginDTO) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getId();
		List<Integer> badge = new ArrayList<>();
		List<UserBadge> badges = userBadgeRepository.findByUser_UserId(userId);
		
		for(UserBadge userBadge : badges){
			badge.add(userBadge.getBadgeId());
		}
		
		return badge;
	}

}
