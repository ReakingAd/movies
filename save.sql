CREATE TABLE media_files (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    -- 基础信息 --
    title VARCHAR(255) NOT NULL COMMENT '资源标题',
    file_type ENUM('video', 'audio', 'image') NOT NULL COMMENT '文件类型',
    
    -- 存储地址信息 --
    origin_url VARCHAR(512) COMMENT '原始爬取URL',
    local_path VARCHAR(512) NOT NULL COMMENT '本地存储路径',
    cdn_url VARCHAR(512) COMMENT 'CDN加速地址',
    
    -- 唯一标识 --
    file_hash CHAR(64) NOT NULL COMMENT 'SHA256文件哈希', 
    imdb_id VARCHAR(20) COMMENT 'IMDB编号',
    
    -- 元数据 --
    duration INT COMMENT '时长(秒)',
    resolution VARCHAR(16) COMMENT '分辨率',
    file_size BIGINT COMMENT '文件大小(字节)',
    
    -- 系统字段 --
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引优化 --
    UNIQUE INDEX idx_hash (file_hash),         -- 哈希值唯一索引
    INDEX idx_type_resolution (file_type, resolution)  -- 组合索引
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;