# 📸 照片管理器

一个现代化的照片管理应用，支持本地照片目录管理、缩略图预览、EXIF信息查看等功能。

## ✨ 功能特性

### 📁 目录管理
- 支持添加本地照片目录到应用
- 自动扫描目录中的图片文件
- 隐藏文件夹过滤（自动跳过以`.`开头的文件夹）
- 目录树结构展示，支持展开/收起子目录

### 🖼️ 图片浏览
- 网格布局展示图片缩略图
- 支持调整缩略图大小（小/中/大/超大）
- 响应式设计，适配不同屏幕尺寸
- 图片懒加载，优化性能

### 📊 图片信息
- 查看图片详细EXIF信息
- 显示拍摄时间、相机型号、GPS位置等
- 支持右键菜单操作

### 🔍 智能分类
- 全部照片视图
- 按目录分类浏览
- 最近导入、收藏夹等快捷入口

## 🛠️ 技术栈

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 现代化构建工具
- **Tailwind CSS** - 实用优先的CSS框架
- **Font Awesome** - 图标库

### 后端
- **Python** - 后端开发语言
- **pywebview** - 桌面应用框架
- **SQLite** - 轻量级数据库
- **Pillow** - 图像处理库

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- pip 包管理器
- npm 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd ImageManage
```

2. **安装后端依赖**
```bash
# 使用uv（推荐）
uv pip install -r requirements.txt

# 或使用pip
pip install -r requirements.txt
```

3. **安装前端依赖**
```bash
cd frontend
npm install
```

4. **启动开发服务器**

**方式一：完整启动（推荐）**
```bash
# 在项目根目录
python backend/main.py
```

**方式二：分别启动**
```bash
# 启动前端开发服务器
cd frontend
npm run dev

# 启动后端（在新终端）
python backend/main.py
```

### 生产环境构建

1. **构建前端**
```bash
cd frontend
npm run build
```

2. **运行应用**
```bash
python backend/main.py
```

## 📁 项目结构

```
ImageManage/
├── backend/                 # 后端代码
│   ├── api.py              # API接口定义
│   ├── database.py         # 数据库操作
│   ├── directory_utils.py  # 目录工具
│   ├── image_utils.py     # 图片处理
│   └── main.py            # 应用入口
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   │   ├── Sidebar.vue     # 侧边栏
│   │   │   ├── PhotoGrid.vue   # 图片网格
│   │   │   └── InfoPanel.vue   # 信息面板
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   └── package.json       # 前端依赖
├── directories.db         # 数据库文件
└── README.md             # 项目文档
```

## 🔧 开发指南

### 添加新功能

1. **后端API开发**
   - 在`api.py`中添加新的API方法
   - 更新数据库模型（如需）
   - 添加相应的工具函数

2. **前端组件开发**
   - 使用Vue 3组合式API
   - 遵循Tailwind CSS样式规范
   - 保持组件的单一职责原则

### 代码规范

- 使用ESLint进行代码检查
- 遵循Vue 3风格指南
- 添加适当的注释和文档

## 🐛 常见问题

### Q: 启动后没有显示已添加的目录？
**A**: 这是因为先启动了前端开发服务器，后启动了Python后端。应用已添加自动重试机制，或者可以手动点击刷新按钮重新加载。

### Q: 缩略图大小调整无效？
**A**: 确保后端能够生成对应尺寸的缩略图，检查图片格式是否受支持。

### Q: 如何添加新的图片格式支持？
**A**: 修改`image_utils.py`中的图片格式白名单。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 提交 [Issue](https://github.com/your-repo/issues)
- 发送邮件到：your-email@example.com

---

**开发时间**: 2024年12月  
**版本**: 1.0.0