# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên (theo tên repo) | Mã sinh viên | Phần đóng góp |
|---|---|---|
| VuBaAnh | 2A202602893 | Harness, chạy thí nghiệm, đánh giá skill và báo cáo |

- Model: `gpt-4o-mini`, nhiệt độ 0.0; endpoint tương thích OpenAI do người dùng cấu hình. Khóa/endpoint không đưa vào báo cáo.
- Python 3.11.16, Deep Agents 0.7.21, Windows với Git Bash; cài editable từ repo. Các hằng số prompt có sẵn giữ nguyên; có phụ chú môi trường Windows áp dụng chung mọi điều kiện.
- Giới hạn graph: lượt baseline học cuối 30; các lượt học subagents chạy lại 40. Các lần khác ghi ở phụ lục. Không có ngân sách token do người dùng chỉ định.
- Commit `freeze`: sẽ điền sau đóng băng.


## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

Các dự đoán được viết trước khi chạy hoặc xem điểm eval.

- H1 (subagents so với baseline): dự đoán subagents không cải thiện điểm eval một cách ổn định, có thể tốn nhiều token hơn. Trên các lượt học ban đầu, `subagent_calls=0`; định nghĩa worker chưa đồng nghĩa với delegation thực sự, và code-learn đã lặp sửa cùng lỗi. Tài liệu Deep Agents giải thích lợi ích cách ly ngữ cảnh chỉ xuất hiện khi công việc được giao qua subagent, đồng thời có overhead: [Subagents](https://docs.langchain.com/oss/python/deepagents/subagents).
- H2 (skills-auto so với baseline): dự đoán skills-auto tăng số check quy ước dùng lại trên eval, nhất là chuẩn hóa service, sắp xếp log và tiền theo cent. Baseline học đạt 0/9 check quy ước; hai skill được giữ cung cấp một phần các quy tắc này. Skill thiếu giá trị schema cụ thể nên dự đoán cải thiện có giới hạn. Cơ chế nạp skill theo tình huống được mô tả trong [Skills](https://docs.langchain.com/oss/python/deepagents/skills).
- H3 (tác vụ học so với tác vụ đánh giá): dự đoán skills-auto có điểm học cao hơn eval vì eval đổi dữ liệu và thêm quy ước mới, theo README mục 2.2. Skill chỉ học phản hồi tập learn, không thể đảm bảo suy ra một quy ước tổ chức mới chưa được cung cấp.


## 3. Làm quen Deep Agents (Phần 0.3)

1. **Bài lab có bao nhiêu agent, mỗi agent làm gì?** Deep Agents mặc định có tác tử chính và subagent `general-purpose`: tác tử chính nhận đề, điều phối và tổng hợp kết quả; `general-purpose` xử lý việc nghiên cứu, tìm kiếm và thực hiện tác vụ nhiều bước. Điều kiện `subagents` yêu cầu định nghĩa thêm ít nhất 2 subagent; tài liệu gợi ý `explorer` (đọc đặc tả, dữ liệu và báo cáo), `implementer` (sửa tệp, chạy test) và `reviewer` (kiểm tra độc lập). Nếu dùng cả 3 vai trò, cấu hình có 1 tác tử chính và 4 loại subagent, tính cả `general-purpose`. Trong repo hiện tại, `get_subagents()` định nghĩa `explorer`, `implementer`, `reviewer`; `build_agent()` thêm chúng ở điều kiện `subagents`. Chế độ `single` vẫn có subagent mặc định `general-purpose`. Curator là bước riêng đọc phản hồi/vết của tác vụ học để sinh skill; bộ chấm `check.py` là mã kiểm tra, không phải agent LLM. Nguồn: `README.md`, `src/lab/agent.py`, `src/lab/subagents.py`, `guides/pseudocode/02_subagents.md`.

2. **Coordinator giao tiếp với worker bằng cách nào?** Tác tử chính gọi tool `task`, chọn `subagent_type` và truyền prompt chứa đề bài, quy tắc, đường dẫn và yêu cầu đầu ra. Theo tour, mỗi lần gọi mặc định là stateless: subagent chỉ thấy prompt được gửi, không tự thấy lịch sử hội thoại của tác tử chính, rồi trả về một báo cáo cuối. Tác tử chính kiểm tra kết quả trước khi dùng và tự tổng hợp câu trả lời cho người dùng. Repo không dùng message queue để giao việc. Nguồn: mô tả tool `task` từ `python scripts/tour.py` và `SUBAGENTS_NOTE`.

3. **Những tool nào được chia sẻ?** Tour ngoại tuyến với Deep Agents 0.7.21 cho thấy tác tử chính có `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute` và `task`. `general-purpose` được mô tả là có cùng công cụ với tác tử chính; các thao tác tệp và shell dùng backend sandbox. `execute` cho phép chạy lệnh shell, Python và test; `task` dùng để giao việc. Bộ công cụ của worker tự định nghĩa sẽ phụ thuộc cấu hình ở Phần 1; không có bằng chứng về công cụ knowledge-base retrieval hoặc logging riêng trong danh sách tour. Nguồn: `scripts/tour.py` và `guides/pseudocode/02_subagents.md`.

**Đối chiếu thêm 3 yêu cầu trong `GUIDE.md` mục 0.3:**

- Danh sách công cụ và công cụ chạy lệnh: như câu 3; công cụ chạy lệnh là `execute`.
- `general-purpose` có thể nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và làm tác vụ nhiều bước; mặc định chỉ nhận prompt giao việc, như câu 2.
- System prompt mà tour ghi nhận là chuỗi rỗng `''`. Một câu hướng dẫn từ `task`: “The agent's report is not shown to the user; relay a summary yourself.” Một câu từ `execute`: “Use read_file rather than cat/head/tail.” Đây là mô tả công cụ mặc định; harness của lab có thêm `BASE_PROMPT` quy định dùng đường dẫn tương đối `workspace/...` cho cả tool tệp và shell.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Chỉ các tác vụ học baseline được dùng. Có 19 check thất bại trên 27 check; 9/9 check `rule_` thất bại (nhóm E). Tỷ lệ check kỹ thuật đạt theo `scripts/check_breakdown.py`: 8/18. Bằng chứng cho thấy lỗi tổ chức là nhóm chiếm nhiều nhất; lỗi kỹ thuật còn ở parsing/rounding và trích xuất log.

| Tác vụ | Check thất bại | Nhóm lỗi | Bằng chứng |
|---|---|---|---|
| code-learn | visible_suite_passes | G | `1 failed, 5 passed` |
| code-learn | tests_not_modified | G | “original files in tests/ must not be modified” |
| code-learn | parse_price_all_formats | D | Sai với `'(12.00)'` |
| code-learn | discount_rounds_half_up | G | Sai các trường hợp `10.05`, `0.05`, `2.665` |
| code-learn | csv_quoting_follows_docstring | G | Kết quả CSV không escape dấu phẩy/ngoặc kép đúng |
| code-learn | rule_type_hints | E | Thiếu type hints cho public functions |
| code-learn | rule_regression_tests | E | Thiếu `tests/test_regressions.py` với ít nhất 3 test |
| code-learn | rule_changelog | E | Thiếu 3 bullet theo mẫu trong `CHANGELOG.md` |
| data-learn | rule_money_in_cents | E | Tiền phải là số nguyên cent |
| data-learn | rule_meta_block | E | Thiếu object `meta` với source/rows_in/rows_used |
| data-learn | rule_clean_csv | E | Thiếu `clean.csv` với header và định dạng quy định |
| logs-learn | entry_count | D | Sai số entry (got 10) |
| logs-learn | timestamps_utc | D | `0/25 timestamps match` |
| logs-learn | exception_fields | D | `25 wrong exception values` |
| logs-learn | repeat_counts | D | `25 wrong repeat_count values` |
| logs-learn | counts_by_service | D | `counts_by_service: wrong values` |
| logs-learn | rule_service_names | E | Service phải lowercase, dấu `-` đổi thành `_` |
| logs-learn | rule_sorted_errors | E | Mảng errors phải sort theo service rồi timestamp UTC |
| logs-learn | rule_schema_header | E | Thiếu `schema_version: 2`, `generated_by: log-triage` |

Phân loại D/G cho check kỹ thuật là diễn giải từ tên check và `detail`; A, B, C, F không được gán nếu trace/check không chứng minh trực tiếp. Skill tổng quát có thể nhắc đọc schema, chuẩn hóa dữ liệu và kiểm tra output; lỗi E có thể giảm nếu quy tắc được cung cấp, nhưng các quy ước này bị ẩn khỏi đề nên khả năng khái quát sang eval cần kiểm chứng.


## 5. Điều kiện `subagents` (Phần 2.3)

Đã định nghĩa `explorer` (chỉ đọc), `implementer` (sửa và kiểm tra), `reviewer` (rà soát độc lập). Trong hai record hoàn tất, `subagent_calls=0`; trace cho thấy coordinator tự gọi các tool chính, không có handoff nên không có nội dung giao việc để đánh giá.

| Tác vụ | Điểm | Token | So với baseline | subagent_calls | error |
|---|---:|---:|---:|---:|---|
| code-learn | 1/10 | 75,817 | baseline 2/10, 29,653 token | 0 | GraphRecursionError ở giới hạn 30 |
| data-learn | 4/8 | 57,684 | baseline 5/8, 63,934 token | 0 | Không |
| logs-learn | chưa có record | — | baseline 1/9, 19,920 token | — | Lượt bị ngắt sau hơn 5 phút; không dùng làm kết quả |

Với data-learn, token thấp hơn 6,250 (9.8%) nhưng điểm thấp hơn 1 check; không thể quy khác biệt cho đa tác tử vì không có subagent handoff và mỗi cấu hình chỉ chạy một lần. Lượt code-learn tiêu tốn nhiều token hơn baseline nhưng đạt thấp hơn và lỗi đệ quy.


## 6. Self-evolving: skill do curator sinh (Phần 3)

Có 3 lượt curator trong giai đoạn chẩn đoán trả metadata không hợp lệ, không ghi được skill. Sau khi sửa prompt yêu cầu lowercase slug, đã chạy thêm 1 lượt và sinh 3 skill. Đây là ngoại lệ so với giới hạn 1 lượt + 2 lần thử lại của GUIDE, được ghi công khai; không diễn giải thành tuân thủ hoàn toàn giới hạn đó.

| Skill | Tổng quát | Tính đúng và hạn chế | Độ dài và description |
|---|---|---|---|
| data-formatting-validation | Áp dụng cho output dữ liệu; không chứa tên tác vụ eval | Đúng về cent nguyên và UTC; nhắc meta nhưng không chỉ rõ rows_in/rows_used và không yêu cầu clean.csv. Ví dụ số tiền là ví dụ từ feedback, không phải đáp án tác vụ. | 9 dòng gồm frontmatter; description khá rộng, phù hợp data validation. |
| error-logging-structure | Áp dụng cho trích xuất log | Đúng về field, UTC, service lowercase/underscore, sort. Thiếu xử lý traceback/repeated lines và giá trị schema_version/generated_by; có thể không đủ đạt các check đó. | 9 dòng gồm frontmatter; description kích hoạt đúng việc xử lý log. |
| test-suite-setup (đã xóa) | Ý định tổng quát cho test | Sai pattern `*_test.py` so với `test_*.py` trong các bài học; có thể chạy 0 test rồi báo thành công. Xóa toàn bộ skill, không sửa nội dung. | 9 dòng; description nói setup test nhưng hướng dẫn chưa phù hợp. |

Hai skill được giữ nguyên byte do curator tạo. Không chỉnh tay nội dung, không dùng dữ liệu eval trong curator. Ba lượt dev đã sao lưu tại results/skills-auto-dev: code-learn 1/10, 27,882 token; data-learn 4/8, 40,171 token; logs-learn 1/9, 22,074 token. Tất cả skills_read=0 ở luồng chính và không có error; chưa có bằng chứng đọc/làm theo skill.


## 7. Kết quả so sánh (Phần 4.3, 4.4)

Chưa tạo `report/table.md` và chưa chạy `check_breakdown.py` cho so sánh cuối. `scripts/check_breakdown.py` hiện báo phần học: baseline kỹ thuật 8/18, house rules 0/9, trung bình 37,835 token; subagents kỹ thuật 5/12, house rules 0/6, trung bình 66,750 token (chỉ 2/3 record). Eval chưa được chạy hoặc đọc. Không thể đóng băng và so sánh `skills-auto` vì curator chưa sinh được skill hợp lệ.


## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

1. Chỉ ba tác vụ học và ba eval với một model gpt-4o-mini; không đủ suy rộng sang model, dữ liệu hoặc tổ chức khác, và không có kiểm định thống kê.
2. Mỗi cấu hình chính chạy một lượt; model ở nhiệt độ 0 vẫn có nhiễu. So sánh dev/post-freeze cùng skill chỉ là ước lượng nhiễu thô, không chứng minh quan hệ nhân quả. Lượt lỗi được thử lại và công khai, nhưng việc thay thế lượt lỗi cũng có thể gây thiên lệch chọn mẫu.
3. Quy ước tổ chức bị ẩn khỏi đề. Curator nhận feedback tập learn và chỉ có thể tái sử dụng phần quy tắc được mô tả; quy tắc eval mới không được skill đảm bảo. Không đưa eval vào curator và không sửa skill sau freeze.
4. Chạy Windows qua Git Bash khác môi trường Linux/WSL/Docker README đề xuất. Phụ chú môi trường áp dụng chung các điều kiện; kết luận chỉ gắn với harness này. API timeout/graph limit phải được xem là yếu tố hạ tầng, không dùng để khẳng định agent suy luận kém.
5. Có một lượt curator bổ sung sau ba lượt metadata không hợp lệ, vượt giới hạn thử lại của GUIDE. Nhật ký ghi đầy đủ; bài không thể được tuyên bố tuân thủ hoàn toàn giới hạn gọi curator.
6. Số token của run.json bao gồm subagent khi được gọi nhưng trace chỉ phản ánh luồng chính; không suy luận bước nội bộ worker từ trace đó. Trung bình chính không bao gồm các lượt debug bị ghi đè, nên không đại diện tổng chi phí toàn bộ quá trình triển khai.


## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh và lần chạy đáng chú ý:
  1. `git fetch origin` và `git merge --ff-only origin/main` → cập nhật tới `ad29c55`.
  2. `.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-final` → **32 passed**.
  3. `.venv\Scripts\python.exe scripts\tour.py` → thành công.
  4. Kiểm tra model bằng endpoint người dùng cấu hình → trả `OK`; không đọc/sửa `.env` và không ghi endpoint hay khóa vào báo cáo.
  5. `baseline/data-learn` chạy thử 4 lần; các lượt đầu chạm recursion limit hoặc tạo đầu ra chưa đúng do sai khác shell Windows. Kết quả lưu cuối: 5/8, 63,934 token, không lỗi.
  6. `baseline/code-learn` → 2/10, 29,653 token; `baseline/logs-learn` → 1/9, 19,920 token.
  7. `subagents/code-learn` → 1/10, 75,817 token, GraphRecursionError ở limit 30; `subagents/data-learn` → 4/8, 57,684 token; `subagents/logs-learn` bị ngắt trước khi ghi record.
  8. Curator chạy 3 lần trên baseline learning outputs; mọi block bị validator loại do tên skill không hợp lệ. Không đọc bất kỳ tác vụ hoặc check nào thuộc eval.
- Trên Windows, backend dùng Git Bash khi có sẵn để hỗ trợ lệnh kiểu `/bin/sh`; WSL/Docker không khả dụng. Backend/runner và prompt curator có thay đổi; toàn bộ test suite vẫn đạt 32/32.
- `.env` không bị sửa hoặc đưa nội dung vào báo cáo. Chưa hoàn tất freeze, eval runs, bảng so sánh và mục 8–10; các phần này phụ thuộc skill hợp lệ và record đầy đủ.
- Số lần chạy tác vụ đã bắt đầu: 9 (gồm một lượt `subagents/logs-learn` bị ngắt); kết quả curator: 3 lần gọi.

### Trước freeze

Đã kiểm tra AST: các hằng số prompt có sẵn, render_trace, main, validate_skill và parse_skill_blocks giữ nguyên so với upstream. Tập eval chưa được chạy hoặc phân tích. Lượt subagents code-learn chạy lại vẫn GraphRecursionError (114,537 token); logs-learn thử lại vẫn API timeout (7,625 token). Đây là dữ liệu lỗi, không dùng để giải thích hiệu quả agent.
