/*
 Navicat Premium Data Transfer

 Source Server         : 150
 Source Server Type    : MySQL
 Source Server Version : 50734
 Source Host           : 10.26.36.10:3306
 Source Schema         : trust

 Target Server Type    : MySQL
 Target Server Version : 50734
 File Encoding         : 65001

 Date: 20/06/2025 17:13:32
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for Resource
-- ----------------------------
DROP TABLE IF EXISTS `Resource`;
CREATE TABLE `Resource`  (
  `resourceId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `osType` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `osVersion` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`resourceId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for log
-- ----------------------------
DROP TABLE IF EXISTS `log`;
CREATE TABLE `log`  (
  `logId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `userId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `terminalId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `logResult` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `logTime` datetime NULL DEFAULT NULL,
  `content` varchar(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`logId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for session
-- ----------------------------
DROP TABLE IF EXISTS `session`;
CREATE TABLE `session`  (
  `sessionId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `startTime` datetime NULL DEFAULT NULL,
  `ResourceId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `UserId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `terminalIP` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Online` int(32) NULL DEFAULT NULL COMMENT '1表示在线，0表示不在线',
  PRIMARY KEY (`sessionId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for terminal
-- ----------------------------
DROP TABLE IF EXISTS `terminal`;
CREATE TABLE `terminal`  (
  `terminalId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `ip` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `terminalType` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `lastLoginUserId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`terminalId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `userId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `userName` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `email` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `phone` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `state` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`userId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for feature
-- ----------------------------
DROP TABLE IF EXISTS `user_feature`;
CREATE TABLE `user_feature`  (
  `userId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `userType` int(11) NULL DEFAULT NULL,
  `threshold` double NULL DEFAULT NULL,
  `loginTotal` int(11) NULL DEFAULT NULL,
  `loginSucceed` int(11) NULL DEFAULT NULL,
  `ifLoginTimeOK` int(11) NULL DEFAULT NULL COMMENT '符合1，不符合0',
  `LoginTimeBias` double NULL DEFAULT NULL,
  `LoginTimeDiff` datetime NULL DEFAULT NULL,
  `ifIpAllow` int(11) NULL DEFAULT NULL,
  `ifAreaAllow` int(11) NULL DEFAULT NULL,
  `score` float NULL DEFAULT NULL COMMENT '信任评估的分值',
  PRIMARY KEY (`userId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

DROP TABLE IF EXISTS `terminal_feature`;
CREATE TABLE `terminal_feature`  (
  `terminalId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `terminalAlert` int(11) NULL DEFAULT NULL,
  `terminalType` int(11) NULL DEFAULT NULL COMMENT '零终端1，瘦终端2，胖终端3',
  `userDiff` int(11) NULL DEFAULT NULL COMMENT '相同1，不同0',
  PRIMARY KEY (`terminalId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

DROP TABLE IF EXISTS `vm_feature`;
CREATE TABLE `vm_feature`  (
  `resourceId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `VMOsAllow` int(11) NULL DEFAULT NULL COMMENT '是1，不是0',
  `VMOsVersionAllow` int(11) NULL DEFAULT NULL COMMENT '是-高危版本系统：1是-低危版本系统：0否：-1',
  `CPU` int(11) NULL DEFAULT NULL COMMENT '是-高危版本系统：1；是-低危版本系统：0；否：-1',
  `mem` int(11) NULL DEFAULT NULL COMMENT '是-高危版本系统：1；是-低危版本系统：0；否：-1',
  `VMConnectionUser` int(11) NULL DEFAULT NULL,
  `VMLoginTotal` int(11) NULL DEFAULT NULL,
  `VMLoginSucceed` int(11) NULL DEFAULT NULL,
  `VMAlert` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`resourceId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

DROP TABLE IF EXISTS `connection`;
CREATE TABLE `connection`  (
  `connectionId` int(11) AUTO_INCREMENT,
  `traceId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `connectStart` datetime NULL DEFAULT NULL,
  `connectEnd` datetime NULL DEFAULT NULL,
  `onlineTime` int(11) NULL DEFAULT NULL,
  `userId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `terminalId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `resourceId` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`connectionId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
