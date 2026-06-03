# P3.12B MP4 Trial Report

## 1. 阶段结论

- MP4 是否生成成功：**是**
- 是否可播放：**是**
- 是否有声音：**是**
- 是否黑屏：**否**
- 是否字幕正常：**基本正常**
- 是否通过 trial：**是**

## 2. 输入候选片

- `outputs/v3_p311c_sales_repair_preview/`

## 3. MP4 本地输出路径

- `outputs/v3_p311c_sales_repair_preview/rendered/final_video.mp4`

## 4. render 命令

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id v3_p311c_sales_repair_preview \
  --output-mode render_mp4 \
  --approved \
  --fps 25
```

## 5. QA 检查表

| 项目 | 结果 | 备注 |
|---|---|---|
| file | PASS | `final_video.mp4` 存在，大小 `7446403` bytes |
| duration | PASS | `75.64s`，与音频 `75.605s` 接近 |
| audio | PASS | 有 audio stream，AAC，单声道，24kHz |
| video | PASS | 有 video stream，H264，`1080x1920`，`25fps` |
| subtitle | PASS | 全程可读，未见明显遮挡主体 |
| content | PASS | hook 前 3 秒可读，中段 proof 可理解，收尾 CTA 出现 |
| CTA | PASS | 最后一帧 CTA 完整、自然 |

## 6. 问题清单

### blocker

- 无

### must-fix

- 无

### nice-to-have

- 中段 `result_summary` 有重复感
- `concept_layers` 连续出现较多，但不影响 trial 通过

## 7. 是否建议作为第一条 publish candidate

- **yes**
- 理由：
  - `approval_status = READY`
  - `semantic_quality` 无 hard fail
  - MP4 可播放且有声音
  - 画面比例正确，CTA 正常收尾
  - sales 候选片是三条里最均衡的一条

## 8. 试验结论

**sales 候选片通过本地 MP4 trial，可作为第一条 publish candidate 进入发布前最终确认。**
