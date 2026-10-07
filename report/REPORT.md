# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Vũ Bá Anh | 2A202602893 | Thực hiện toàn bộ bài lab cá nhân: triển khai, chạy thí nghiệm, phân tích và viết báo cáo. |

- Ngân sách token/tiền: chưa xác định vì chưa được cung cấp hoặc quy định trong tài liệu root.
- Môi trường chạy đã xác minh: Docker Desktop Linux/amd64, Python 3.12.15, Deep Agents 0.7.21, môi trường ảo và `pip install -e .`. Repo máy chủ là bản chính; đồng bộ bằng `docker cp` vì ổ E: không mount được. `.venv` Windows không dùng được; ghi chép Windows/Git Bash trước đây là lịch sử thử nghiệm, không phải môi trường CP4.
- Cấu hình hiện tại và các lần CP4 mới: `LAB_MODEL=openai:gpt-4o-mini`, `LAB_TEMPERATURE=0`, `--recursion-limit 40`. CP3 kiểm tra bộ skill cuối cũng dùng limit 40. `run.json` cũ không lưu model/temperature; chỉ có ghi chép limit 30/40 và thông báo lỗi limit 40 ở một số run, nên không gán cấu hình hiện tại cho từng run cũ.
- Có 18 cặp `run.json`/`trace.md` chính thức; thư mục `results/failed-attempts/` còn 6 `run.json` của lượt lỗi, lưu riêng và có thể trùng bản sao ở archive/staging, nên không cộng chúng thành số lượt độc lập. Lệnh được ghi nhận rõ ở CP2–CP4 gồm 1 task CP2, 3 task CP3 sau freeze và 4 task CP4, tức 8 lượt phát sinh gần đây; ba learn CP3 sau freeze được sao vào vị trí chính thức, không tính thêm ba lần. Các lượt thử trước đó và tổng lần gọi API toàn lịch sử chưa xác minh được. Tổng token đã chi trả và ngân sách không suy từ 18 artifact vì còn lần thử/backup.
- Commit `hypotheses`: `d0023cd3705815b5ede8f8357d8f74d4b2ac3357`; commit/tag `freeze`: `9988c5c056b080947e6d3622e35da8d33ae18daf`. Không đưa khóa API hoặc endpoint vào báo cáo.


## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

Ba dự đoán dưới đây khớp nguyên văn commit `hypotheses`, trước tag `freeze` và trước timestamp eval sớm nhất hiện có. Thứ tự commit/timestamp không chứng minh tuyệt đối chưa từng xem điểm eval; nhận xét sau thí nghiệm nằm ở mục 8.

- H1 (subagents so với baseline): dự đoán subagents không cải thiện điểm eval một cách ổn định, có thể tốn nhiều token hơn. Trên các lượt học ban đầu, `subagent_calls=0`; định nghĩa worker chưa đồng nghĩa với delegation thực sự, và code-learn đã lặp sửa cùng lỗi. Tài liệu Deep Agents giải thích lợi ích cách ly ngữ cảnh chỉ xuất hiện khi công việc được giao qua subagent, đồng thời có overhead: [Subagents](https://docs.langchain.com/oss/python/deepagents/subagents).
- H2 (skills-auto so với baseline): dự đoán skills-auto tăng số check quy ước dùng lại trên eval, nhất là chuẩn hóa service, sắp xếp log và tiền theo cent. Baseline học đạt 0/9 check quy ước; hai skill được giữ cung cấp một phần các quy tắc này. Skill thiếu giá trị schema cụ thể nên dự đoán cải thiện có giới hạn. Cơ chế nạp skill theo tình huống được mô tả trong [Skills](https://docs.langchain.com/oss/python/deepagents/skills).
- H3 (tác vụ học so với tác vụ đánh giá): dự đoán skills-auto có điểm học cao hơn eval vì eval đổi dữ liệu và thêm quy ước mới, theo README mục 2.2. Skill chỉ học phản hồi tập learn, không thể đảm bảo suy ra một quy ước tổ chức mới chưa được cung cấp.


## 3. Làm quen Deep Agents (Phần 0.3)

1. Tour liệt kê `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` là công cụ chạy lệnh.
2. `general-purpose` xử lý nghiên cứu, tìm kiếm và tác vụ nhiều bước. Theo output tour CP0, mỗi lần gọi mặc định chỉ nhận prompt được giao, không tự nhận lịch sử hội thoại của tác tử chính.
3. System prompt mặc định rỗng. Output tour ghi trong mô tả `task`: “The agent's report is not shown to the user; relay a summary yourself.” Trong mô tả `execute`: “Use read_file rather than cat/head/tail.”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Chỉ các tác vụ học baseline được dùng. Có 19 check thất bại trên 27 check; 9/9 check `rule_` thất bại (nhóm E). Tỷ lệ check kỹ thuật đạt theo `scripts/check_breakdown.py`: 8/18. Bằng chứng cho thấy lỗi tổ chức là nhóm chiếm nhiều nhất; lỗi kỹ thuật còn ở parsing/rounding và trích xuất log.

| Tác vụ | Check thất bại | Nhóm AG | Bằng chứng từ detail/trace |
|---|---|---|---|
| code-learn | visible_suite_passes | G | Detail checker nguyên văn: `1 failed, 5 passed in 0.18s`. Riêng trace ghi ba lệnh `unittest discover` do agent chạy đều dừng với `ImportError: Start directory is not importable: 'tests'`; đây là kết quả khác, không xác định nguyên nhân của detail checker. |
| code-learn | tests_not_modified | G | Detail nguyên văn: `the original files in tests/ must not be modified (new test files are allowed)`. Checker đánh giá workspace tác vụ trong sandbox; detail mô tả điều kiện, không chứng minh repo người dùng đã bị sửa. Trace không ghi thao tác ghi vào `tests/`, nên chưa xác định nguyên nhân check thất bại. |
| code-learn | parse_price_all_formats | D | Detail: sai với `'(12.00)'`; trace cho thấy sửa `parse_price` để bỏ dấu phẩy nhưng không xử lý dạng ngoặc kế toán. |
| code-learn | discount_rounds_half_up | D | Detail: sai với `10.05`, `0.05`, `2.665`; trace dùng `Decimal.quantize` mặc định, không thể hiện quy tắc half-up. |
| code-learn | csv_quoting_follows_docstring | D | Detail trả `Desk, large "oak",10.00,2`; trường CSV chứa dấu phẩy/ngoặc kép chưa được quote đúng. |
| code-learn | rule_type_hints | E | Detail RULE yêu cầu annotation cho mọi tham số và giá trị trả về của hàm public. |
| code-learn | rule_regression_tests | E | Detail RULE yêu cầu `tests/test_regressions.py`, mỗi lỗi một test và ít nhất 3 test. |
| code-learn | rule_changelog | E | Detail RULE yêu cầu ít nhất 3 bullet theo mẫu trong `CHANGELOG.md` dưới `## Unreleased`. |
| data-learn | rule_money_in_cents | E | Detail RULE yêu cầu số tiền trong `answer.json` là integer cents. |
| data-learn | rule_meta_block | E | Detail RULE yêu cầu object `meta` có `source`, `rows_in`, `rows_used`. |
| data-learn | rule_clean_csv | E | Detail RULE yêu cầu `clean.csv` với header, dòng, UTC, region canonical và cents theo quy ước. |
| logs-learn | entry_count | D | Detail: `wrong number of entries (got 10)`. |
| logs-learn | timestamps_utc | D | Detail: `0/25 timestamps match`; trace đọc log theo trang nhưng đầu ra không chuẩn hóa timestamp nhất quán. |
| logs-learn | exception_fields | D | Detail: `25 wrong exception values`; trace chỉ giữ một số traceback và có entry không gắn exception đúng. |
| logs-learn | repeat_counts | D | Detail: `25 wrong repeat_count values`; trace/output không tính đúng các dòng repeated. |
| logs-learn | counts_by_service | D | Detail: `counts_by_service: wrong values`, phù hợp với số entry/repeat bị sai. |
| logs-learn | rule_service_names | E | Detail RULE yêu cầu lowercase và đổi `-` thành `_`. |
| logs-learn | rule_sorted_errors | E | Detail RULE yêu cầu sort theo service rồi timestamp UTC tăng dần. |
| logs-learn | rule_schema_header | E | Detail RULE yêu cầu `schema_version: 2` và `generated_by: log-triage`. |

Trong baseline learn có 19 check thất bại: E=9, D=8, G=2; không có bằng chứng đủ để gán A, B, C hoặc F. E là nhóm nhiều nhất. Mẫu chung là đầu ra chưa tuân quy ước tổ chức ẩn khỏi đề; ngoài ra tác vụ log cho thấy xử lý dữ liệu/định dạng và kiểm chứng kết quả chưa đủ. Một skill có thể nhắc đối chiếu schema, quy tắc định dạng, tính toán trên toàn bộ dữ liệu và đọc lại/kiểm tra đầu ra trước khi báo xong; điều đó có thể giúp các quy ước đã biết, nhưng không thể bảo đảm các quy ước ẩn chưa được cung cấp. Đây là đề xuất phân tích, không phải skill đã tạo.

Các check kỹ thuật baseline đạt `8/18`; đây là bằng chứng phủ định cho việc quy toàn bộ lỗi thành A–D, nhưng không chứng minh tác tử chưa từng bỏ qua đặc tả, thiếu kiểm chứng hoặc vá triệu chứng. `visible_suite_passes` và `tests_not_modified` vẫn thuộc G vì chưa xác định được nguyên nhân trực tiếp. Lỗi import của các lệnh unittest agent tự chạy không được dùng làm bằng chứng lỗi tác tử hay thay thế detail checker. Check `tests_not_modified` nói về workspace sandbox của bài; không diễn giải thành người dùng sửa `tests/` hoặc `tasks/` trong repo.


## 5. Điều kiện `subagents` (Phần 2.3)

Ba subagent được định nghĩa trong repo: `explorer` dùng khi cần kiểm tra repo/dữ liệu trước khi sửa, chỉ đọc và báo cáo bằng chứng; `implementer` dùng cho thay đổi code/dữ liệu có phạm vi độc lập, sửa và chạy check; `reviewer` dùng để rà độc lập tính đúng, yêu cầu bị sót và edge case, không sửa file. Lý do thiết kế là tách khảo sát, thực hiện và review thành các vai trò có ranh giới rõ. `description` nêu điều kiện gọi; `system_prompt` giới hạn phạm vi, và `build_agent` bổ sung `PATHS_NOTE` cho từng subagent. Đây là thiết kế trong mã, không phải bằng chứng chúng đã được gọi.

| Task | Điều kiện | Nguồn record | Điểm/check đạt | Tokens.total | seconds | subagent_calls | error |
|---|---|---|---:|---:|---:|---:|---|
| code-learn | baseline | Tái sử dụng | 2/10 | 29,653 | 21.8 | 0 | null |
| code-learn | subagents | Tái sử dụng | 1/10* | 114,537* | 41.0* | 0 | Dừng ở limit 40: `GraphRecursionError` |
| data-learn | baseline | Tái sử dụng | 5/8 | 63,934 | 57.8 | 0 | null |
| data-learn | subagents | Tái sử dụng | 4/8 | 57,684 | 22.1 | 0 | null |
| logs-learn | baseline | Tái sử dụng | 1/9 | 19,920 | 19.4 | 0 | null |
| logs-learn | subagents | Chạy mới một lần | 1/9 | 19,746 | 11.5 | 0 | null |

| Task eval | Điểm/check đạt | Tokens.total | seconds | subagent_calls | error |
|---|---:|---:|---:|---:|---|
| code-eval | 1/11* | 118,196* | 74.6* | 0 | `GraphRecursionError` limit 40 |
| data-eval | 1/9 | 45,583 | 18.2 | 0 | null (lượt 429 cũ đã lưu riêng) |
| logs-eval | 1/10 | 18,677 | 11.5 | 0 | null |

Cả sáu run `subagents` có `subagent_calls=0`; sáu trace luồng chính không có tool call `task`, nên số lần gọi theo từng loại (`explorer`, `implementer`, `reviewer`, `general-purpose`) đều là 0. Ba eval cho thấy tác tử chính tự dùng các tool: code-eval lặp `edit_file`, data-eval dùng `read_file`/`execute`, logs-eval dùng `read_file`/`write_file`. Không có prompt giao việc, kết quả worker hay bước kiểm chứng worker để đối chiếu. Ba learn đã có đủ `run.json` và `trace.md`; `subagents/logs-learn` được chạy bổ sung một lần sau khi lưu riêng lỗi `OpenAITimeoutError`. Với `subagents/code-learn`, trace cho thấy agent liên tục sửa `export.py` rồi chạy unittest; các lần cuối vẫn báo `SyntaxError: unterminated string literal` ở dòng 12 và trace kết thúc sau một lần `edit_file` khác. Một giải thích khả dĩ (suy luận từ luồng thao tác, không phải lý do model xác nhận) là agent coi thay đổi này đủ hẹp để tiếp tục tự sửa và kiểm tra; lý do thực tế không được ghi lại.

`subagents/code-learn` và `subagents/code-eval` bị dừng ở recursion limit 40; record vẫn được giữ. Dấu `*` trong hai bảng đánh dấu điểm, token và thời gian của lần bị dừng; mọi trung bình subagents gồm cả hai lần này. Vì `subagent_calls=0`, mức tăng token của code-learn không thể được gọi là chi phí giao việc.

So sánh chi phí subagents trừ baseline theo task: code `+84,884` token (`+286.1%`) và `+19.2` giây (`+88.1%`); data `−6,250` token (`−9.8%`) và `−35.7` giây (`−61.8%`); logs `−174` token (`−0.9%`) và `−7.9` giây (`−40.7%`). Đây là so sánh mô tả của một lần chạy mỗi điều kiện; code-learn của subagents bị dừng và cả ba task đều không có lần gọi subagent, nên không quy chênh lệch token cho giao việc.

Về cấu hình từng lượt: mục 1 của báo cáo ghi nhận ở mức cấu hình chung `gpt-4o-mini`, temperature 0, nhưng run.json/trace không gắn model hoặc temperature với từng artifact; do đó không xác minh độc lập được hai tham số này cho từng lần chạy và không suy ra từ `.env` hiện tại. Báo cáo ghi baseline learn cuối dùng limit 30; run.json của `subagents/code-learn` nêu rõ limit 40; lệnh chạy bổ sung `subagents/logs-learn` trong phụ lục có `--recursion-limit 40`. Limit riêng của `subagents/data-learn` và các lượt không có lệnh/record chỉ rõ chưa xác minh được. Dòng lịch sử nói “mọi lượt chính thức” dùng 40 mâu thuẫn với ghi chép baseline limit 30; không sửa số liệu lịch sử để làm chúng đồng nhất. Chênh lệch 30/40 làm giảm khả năng quy chênh lệch cho riêng điều kiện thí nghiệm.

`*` Lần `subagents/code-learn` bị dừng ở limit 40 vẫn nằm trong mẫu thống kê. Chỉ xét sáu artifact learn: baseline có kỹ thuật `8/18`, rule_ `0/9`, trung bình `37,835.7` token/run và `33.0` giây/run; subagents có kỹ thuật `6/18`, rule_ `0/9`, trung bình `63,989` token/run và `24.9` giây/run, bao gồm lần code-learn bị dừng (`114,537` token, `41.0` giây). `check_breakdown.py` đã chạy sau freeze; output đầy đủ ở mục 7. GraphRecursionError được ghi nhận là lần chạy bị dừng, không dùng để gán lỗi hành vi tác tử hoặc chọn kết quả khác.


## 6. Self-evolving: skill do curator sinh (Phần 3)

Tag `freeze` trỏ tới commit `9988c5c056b080947e6d3622e35da8d33ae18daf`, thời điểm commit `2026-10-06T17:22:20+07:00`. Commit `hypotheses` là `d0023cd3705815b5ede8f8357d8f74d4b2ac3357`, thời điểm `2026-10-06T17:22:08+07:00`, ancestor của freeze và sớm hơn 12 giây; commit này có H1, H2, H3 đã điền và thêm hai SKILL.md hiện tại. Cây `skills/auto/` hiện tại khớp tag. Đây chứng minh thứ tự commit và nội dung giả thuyết trước tag, không chứng minh thời điểm chúng được viết ngoài lịch sử commit.

Về nguồn gốc skill, `results/EXPERIMENT_NOTES.md` (đã có trong commit `hypotheses`) ghi ba lượt curator đầu không ghi skill vì metadata sai, rồi một lượt bổ sung sinh ba skill; ghi chú tự nhận đã vượt giới hạn chạy lại. Commit `hypotheses` xác nhận hai skill hiện tại được thêm cùng commit với giả thuyết, nhưng không ghi công cụ tạo file. Không tìm thấy log/prompt/output curator thô để đối chiếu ghi chú này. Vì vậy đây là bằng chứng tự thuật cụ thể hơn về chuỗi lượt, không phải xác nhận độc lập nguồn gốc hoặc việc dùng dữ liệu eval; cũng không phải bằng chứng skill bị sửa tay. RUBRIC không quy định phải lưu log thô.

Ghi chú phụ lục cũ nói ba lần gọi có block bị validator loại; `EXPERIMENT_NOTES.md` mô tả rõ hơn là ba lượt đầu lỗi metadata rồi một lượt sau sinh ba skill, đồng thời tự nhận vượt giới hạn tối đa hai lần chạy lại của GUIDE. Có thể trình bày đây là lời tự khai về bốn lượt tổng cộng (ba lượt lỗi và một lượt bổ sung), nhưng không có log để xác nhận số CLI invocation/model call, thời điểm lỗi so với model call hay số lần chạy lại theo nghĩa vận hành. Không có bằng chứng độc lập để nâng lời tự khai thành kết luận đã kiểm chứng. Từ CP3 đến CP5 không gọi thêm curator.

Hai skill hiện tại được kiểm tra bằng `validate_skill` với kết quả rỗng cho cả hai; report ghi test helper đạt 2/2. Kiểm tra nội dung chỉ dùng feedback/task learn và tài liệu kỹ thuật; không mở nội dung eval. `validate_skill` chỉ dùng danh sách ID/tên file eval để quét marker, không đọc nội dung task eval. Đánh giá chất lượng bên dưới áp dụng cho nội dung hiện có; tính hợp lệ định dạng và đánh giá nội dung không tự chứng minh nguồn gốc curator.

| Skill | Validation | Tổng quát, đúng/sai và hạn chế | Dòng; description | SHA-256 file |
|---|---|---|---|---|
| `data-formatting-validation` | Hợp lệ | Quy trình dữ liệu tổng quát: integer cents, UTC, kiểm tra field/schema. Thiếu chi tiết `rows_in`/`rows_used` và yêu cầu `clean.csv`. Ví dụ `1606.67 USD → 160667` lặp lại ví dụ trong feedback RULE; không phải đáp án từ dữ liệu nhưng là con số cụ thể không cần thiết, có nguy cơ làm skill kém tổng quát. | 9 dòng; description dùng khi kiểm tra định dạng dữ liệu và tuân đặc tả, khá rộng nhưng đúng tình huống. | `3B7362E5A048664A61D0029739C2B6B3A19C6E1EE6CFAA9DD7B2CEC5DC48A32F` |
| `error-logging-structure` | Hợp lệ | Khớp quy tắc lowercase/underscore, UTC, sort và có hai khóa schema. Chưa nêu giá trị bắt buộc `schema_version=2`, `generated_by=log-triage`, cách lấy exception từ traceback hoặc cộng `repeat_count`; đúng hướng nhưng chưa đủ bao phủ feedback learn. | 9 dòng; description nêu rõ dùng khi cấu trúc và sắp xếp error log, phù hợp. | `D289E196902D09F4F5E7C06EC7122C691F842317F8AE9E19DE90ACAAEB5E09FB` |

`test-suite-setup` là skill được ghi nhận đã loại trong report; không còn file để kiểm tra lại. Bộ skill hiện tại có hash `0612381bb302045aceb44d137388f7332c9aecf83f58ff041690665f5faffaf0` theo `hash_skills`; cả ba run audit dưới đây ghi đúng hash này và `skills_modified=false`.

| Task learn | Điểm/check đạt | Tokens.total | seconds | skills_read | skills_modified | error |
|---|---:|---:|---:|---:|---|---|
| code-learn | 4/10 | 52,169 | 22.7 | 0 | false | null |
| data-learn | 2/8 | 56,694 | 38.7 | 0 | false | null |
| logs-learn | 0/9 | 30,738 | 180.1 | 0 | false | null |

Các record trong bảng được chạy sau tag freeze, với `recursion_limit=40`, rồi sao nguyên vào `results/skills-auto/` ở CP4; không được coi là lần dev trước freeze hay một phép đo thứ hai. Ba record cũ tại `results/skills-auto-dev/` có cùng hash đầy đủ `2e16756003276761a6d85ba49d248033400488b016c6c852904dba1884780153`, `skills_modified=false`, `skills_read=0`, `error=null`; timestamp UTC lần lượt là 10:20:35.662708, 10:20:53.661507, 10:21:26.477957 ngày 2026-10-06, với `seconds` 15.7, 32.5, 14.0. Vì vậy cả ba kết thúc trước thời điểm freeze 10:22:20 UTC. Không tìm thấy bundle hash `2e167...` trong lịch sử Git hoặc bản sao lưu hiện có; không thể tái tạo bundle để xác minh hash bằng `hash_skills`. Chúng chứng minh ba lần learn trước freeze thuộc cùng một hash chưa nhận diện, không chứng minh đó là bộ skill hiện tại. Sáu run hash cũ từng ở `results/skills-auto/` đã được lưu tại `results/cp4-archive-20261006/skills-auto-original/`.

Bản audit mới được lưu riêng tại `results/skills-auto-dev-final-0612381b/`, cùng hash bộ skill cuối `0612381bb302045aceb44d137388f7332c9aecf83f58ff041690665f5faffaf0` đã xác minh bằng `hash_skills`, và chạy sau freeze. Đây là ba lần kiểm tra sau freeze cùng bộ skill hiện tại; chúng không thay thế lần CP3.4 trước freeze. Do chưa có CP3.4 pre-freeze có hash `0612381...`, chưa có cặp cùng-bộ-skill trước/sau để ước lượng nhiễu cho bộ cuối. Cặp dữ liệu cùng hash `2e167...` chỉ có thể mô tả cohort cũ chưa xác định được skill, không thể dùng để đo nhiễu của bộ cuối.

Không run nào đọc skill: cả ba `run.json` ghi `skills_read=0`, và trace chỉ cho thấy đọc file task (code: các module inventory; data: README/CSV; logs: app.log), không có đường dẫn `skills/...`. Vì vậy không có bằng chứng skill được áp dụng. So với baseline: code có hai check chuyển từ fail sang pass (`visible_suite_passes`, `discount_rounds_half_up`), nhưng `low_stock_follows_docstring` chuyển từ pass sang fail; các rule vẫn fail. Data không có check nào cải thiện; `north_q1_revenue`, `north_q1_orders`, `missing_amount_orders` chuyển từ pass sang fail, còn ba rule vẫn fail. Logs không có check cải thiện; `valid_structure` chuyển từ pass sang fail và các check còn lại vẫn fail. Detail logs báo `FileNotFoundError` cho `workspace/errors.json`; `run.json.error=null`, nên ghi nhận đây là kết quả checker của lần chạy, không phải lỗi API. Những thay đổi điểm này không thể quy cho skill vì không skill nào được đọc.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Nội dung `report/table.md` do `python -m lab.compare` sinh trực tiếp từ 18 `run.json` chính thức (mỗi run đều có `trace.md`):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 2/10 | 1/10 | 4/10 |
| data-learn | 5/8 | 4/8 | 2/8 |
| logs-learn | 1/9 | 1/9 | 0/9 |
| code-eval | 0/11 | 1/11 | 0/11 |
| data-eval | 2/9 | 1/9 | 3/9 |
| logs-eval | 1/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.31 | 0.24 | 0.22 |
| **Mean score - evaluation tasks** | 0.11 | 0.10 | 0.14 |
| **Mean tokens per run** | 53,255 | 62,403 | 35,114 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Output `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      3/18         0/12          68,674      0/3
baseline      learn     8/18         0/9           37,835      0/3
subagents     eval      3/18         0/12          60,818      0/3
subagents     learn     6/18         0/9           63,989      0/3
skills-auto   eval      4/18         0/12          23,694      0/3
skills-auto   learn     6/18         0/9           46,533      0/3
```

Nguồn artifact: sáu `baseline` và năm `subagents` được tái sử dụng; `subagents/data-eval` cũ lỗi API 429 được lưu tại `results/cp4-archive-20261006/subagents-data-eval-original/`, rồi chạy mới đúng một lần (1/9, 45.583 token, `error=null`). Ba learn của bộ skill cuối được sao chép nguyên `run.json`/`trace.md` từ `results/skills-auto-dev-final-0612381b/` sang `results/skills-auto/`, có đối chiếu SHA-256 từng file; đây là **cùng run sau freeze**, không phải phép đo độc lập. Sáu artifact `skills-auto` hash cũ được bảo toàn tại `results/cp4-archive-20261006/skills-auto-original/`. Ba eval `skills-auto` chạy mới một lần mỗi task với `--recursion-limit 40`, dùng bộ skill cuối hash `0612381bb302045aceb44d137388f7332c9aecf83f58ff041690665f5faffaf0`; cả sáu run chính thức của điều kiện này ghi `skills_modified=false` và hash đó.

Các record bị dừng vẫn nằm trong bảng: `baseline/code-eval`, `subagents/code-learn` và `subagents/code-eval` ghi `GraphRecursionError` limit 40. `skills-auto/code-eval` đạt 0/11 nhưng `error=null`; đây là kết quả checker, không phải lỗi API. Lượt 429 cũ chỉ ở backup, không được trộn vào số liệu chính thức. `verify_freeze.py` lúc đầu báo sáu run `skills-auto` dùng hash cũ (và một chênh lệch xuống dòng Git chỉ trong container); sau khi đưa đúng cohort vào vị trí chính thức, output là `checked 6 runs of skill conditions: OK`.

Commit `hypotheses` lúc `2026-10-06T17:22:08+07:00` đứng trước tag `freeze` lúc `17:22:20+07:00`. Metadata của mọi eval hiện có bắt đầu sau hai mốc này; thời điểm sớm nhất là `2026-10-06T10:24:19.965956+00:00`. Đây là timestamp do runner ghi, không xác minh được người viết giả thuyết chưa từng thấy điểm eval trước commit. Model/temperature của các run cũ không có trong `run.json`, nên không suy từ `.env` hiện tại; các run mới dùng cấu hình hiện tại được cung cấp (`openai:gpt-4o-mini`, nhiệt độ 0) và lệnh limit 40. Giới hạn 30/40 ở các run learn cũ làm so sánh điều kiện kém đồng nhất. Thiếu bằng chứng curator và bundle hash `2e167...` trước freeze vẫn như mục 6. Không có run CP3.4 trước freeze của bộ skill cuối; không lấy chênh lệch giữa hash cũ và hash cuối làm nhiễu, cũng không coi bản sao của cùng run là hai phép đo.


## 8. Phân tích

Điểm trung bình dưới đây là trung bình số học của ba phân số `passed/total` theo từng vai trò, không tính từ hai chữ số đã làm tròn trong bảng mục 7. Mỗi tác vụ có trọng số bằng nhau; các run bị dừng vẫn được tính.

1. **Learn và eval; đối chiếu H1–H3.** Learn: baseline `0,312037`, subagents `0,237037` (−7,50 điểm phần trăm), skills-auto `0,216667` (−9,54 điểm phần trăm); không điều kiện nào tăng điểm learn. Eval: baseline `0,107407`, subagents `0,100673` (−0,67 điểm phần trăm), skills-auto `0,144444` (+3,70 điểm phần trăm). Không có trường hợp tăng learn nhưng không tăng eval trong 18 run này. H1 phù hợp phần điểm eval subagents không tăng, nhưng dự đoán tốn token hơn không đúng ở riêng eval (60.818,7 so với 68.674,7 token/run); cả sáu lần đều không delegate nên không kiểm định lợi ích của phối hợp đa tác tử. H2 dự đoán tăng check quy ước eval, trái với `0/12` của cả ba điều kiện. H3 dự đoán skills-auto học cao hơn eval: `0,216667 > 0,144444`, phù hợp chiều dự đoán; một lần mỗi task và chênh lệch độ khó không cho phép suy nguyên nhân. Mọi chênh lệch ở đây là **điểm phần trăm**, không phải phần trăm tương đối.

2. **Kỹ thuật và quy ước.** Số check kỹ thuật đạt ở learn lần lượt là baseline `8/18`, subagents `6/18`, skills-auto `6/18`; ở eval là `3/18`, `3/18`, `4/18`. Check `rule_` của cả ba điều kiện đều `0/9` learn và `0/12` eval. Vì vậy không quan sát được skill giúp đạt bất kỳ quy ước nào, kể cả quy ước mới của eval. Sáu run skills-auto ghi `skills_read=0`; nội dung skill có nhắc một số quy tắc learn nhưng không có bằng chứng nó được nạp và thực hiện. Check kỹ thuật tăng thêm một ở eval là quan sát của điều kiện, không phải hiệu quả đã xác nhận của skill.

3. **Cơ chế từ check và trace.** Không thể nêu một check *do áp dụng skill* mà đạt: không run skills-auto nào đọc skill và trace không ghi lượt mở `skills/...`. Ví dụ `code-learn/discount_rounds_half_up` đổi từ fail ở baseline sang pass ở skills-auto, còn `data-learn/north_q1_revenue` đổi từ pass sang fail; đó chỉ là chuyển trạng thái check. `data-eval/duplicate_events_removed` fail ở baseline nhưng pass ở cả subagents và skills-auto, cũng không chỉ ra tác dụng riêng của skill. Ở `logs-learn`, `valid_structure` từ pass thành fail; detail của skills-auto là thiếu `workspace/errors.json` dù `error=null`, và trace không có lượt đọc skill để giải thích bằng việc làm theo skill. `skills_read=0` không có nghĩa prompt/context của skills-auto giống hệt baseline: `build_agent` bật `skills` và thêm `SKILLS_NOTE`, còn quỹ đạo tool có thể khác. Vì vậy cũng không quy mọi chênh lệch chỉ cho nhiễu.

4. **Token và hiệu quả.** Trung bình token/run theo learn, eval, rồi cả sáu lần: baseline `37.835,7 / 68.674,7 / 53.255,2`; subagents `63.989,0 / 60.818,7 / 62.403,8`; skills-auto `46.533,7 / 23.694,7 / 35.114,2`. Định nghĩa proxy hiệu quả là `trung bình điểm chuẩn hóa / trung bình tokens.total × 1.000` cho cùng cohort. Kết quả theo learn/eval/toàn bộ: baseline `0,008247 / 0,001564 / 0,003938`; subagents `0,003704 / 0,001655 / 0,002706`; skills-auto `0,004656 / 0,006096 / 0,005142` điểm trên 1.000 token. Skills-auto đứng đầu proxy toàn bộ và eval, baseline đứng đầu learn. Đây không phải giá USD: token input/output, cache và model của từng lượt cũ chưa được xác minh đủ để tính tiền. `baseline/code-eval`, `subagents/code-learn`, `subagents/code-eval` dừng do `GraphRecursionError` ở limit 40; ghi chép còn có limit 30 ở lượt learn cũ, nên thời gian/token và điểm giữa điều kiện không đồng nhất hoàn toàn. Với `subagent_calls=0` cả sáu lần, cấu hình subagents trong thí nghiệm này tăng token trung bình toàn bộ và giảm điểm trung bình toàn bộ so với baseline; dữ liệu không đo chi phí/lợi ích của delegation thực sự.

5. **Quá khớp và rò rỉ.** Skill học từ feedback learn nên rủi ro quá khớp với quy tắc learn và việc xem eval trước freeze là rủi ro rò rỉ; ví dụ số tiền cụ thể trong skill dữ liệu làm độ tổng quát đáng xem xét. Hai skill hiện tại hợp lệ, hash khớp freeze, sáu run chính thức ghi `skills_modified=false` và eval hiện có đều có timestamp sau freeze. Hash cũ `2e167...` khác hash cuối chỉ chứng minh hai bundle khác nhau, không chứng minh rò rỉ. Không có log curator độc lập và thứ tự commit/timestamp không chứng minh tuyệt đối chưa từng xem eval; cũng không có bằng chứng xác nhận sửa tay hay vi phạm. Vì `skills_read=0` và không có cải thiện learn/eval đáng tin do skill được áp dụng, điểm số đơn thuần không chứng minh skill overfit. Bảo toàn cohort cũ, backup lượt 429 và artifact cuối giúp kiểm toán phần lịch sử còn lại.

6. **Nhiễu.** Không có hai phép đo độc lập trước/sau freeze với *cùng bộ skill cuối*. Ba learn `results/skills-auto-dev/` trước freeze mang hash `2e167...`, khác hash cuối `061238...`; bundle cũ cũng không tìm thấy để kiểm tra lại. Ba learn ở `results/skills-auto-dev-final-0612381b/` và ba learn chính thức là bản sao byte của **cùng run sau freeze**, nên chênh lệch giữa chúng bằng 0 theo định nghĩa sao chép, không phải nhiễu bằng 0. Vì thế không tính được chênh lệch điểm dùng làm ước lượng nhiễu của bộ cuối; độ tin cậy của chênh lệch nhỏ ở mục 7 chưa được định lượng. Phần yêu cầu đo lặp này của RUBRIC 6.2 **chưa đáp ứng đầy đủ** và không thể khắc phục bằng viết lại báo cáo.

## 9. Hạn chế và tính hợp lệ

1. Chỉ ba task mỗi vai trò, một kết quả chính thức cho mỗi task/condition. Mẫu nhỏ, không có sai số đo lặp nên chênh lệch 0,67–3,70 điểm phần trăm ở eval không chứng minh hiệu quả ổn định hoặc suy rộng sang dữ liệu khác.
2. Sáu run subagents không gọi `task`; sáu run skills-auto không đọc skill. Với model nhỏ `openai:gpt-4o-mini` ở các lượt mới và thất bại kỹ thuật trong checker, kết quả kiểm tra cấu hình được bật nhưng chưa kiểm tra tác động khi worker/skill thực sự được dùng. Model/temperature của lượt cũ thiếu metadata nên không chứng nhận mọi run dùng cùng mô hình.
3. Ba run chính thức bị dừng ở limit 40; ghi chép learn cũ có cả limit 30, còn lượt 429 được thay sau khi lưu backup. Kết quả từng lần và token trung bình chịu ảnh hưởng của điểm dừng, giới hạn không đồng nhất và lựa chọn lượt thay; không thể quy riêng chênh lệch cho điều kiện.
4. Thiếu lần đo CP3.4 trước freeze của bộ skill cuối; bản sao sau freeze không phải lặp độc lập. Vì vậy không ước lượng được nhiễu cùng skill, kể cả ở nhiệt độ 0. Các quy ước eval mới cũng chưa nằm trong feedback learn, làm việc suy rộng quy tắc khó kiểm chứng.
5. `results/EXPERIMENT_NOTES.md` tự ghi ba lượt metadata lỗi, một lượt bổ sung sinh ba skill và tự nhận vượt giới hạn chạy lại; không có log thô để kiểm chứng độc lập invocation, model call hoặc thứ tự lỗi/call. Đây là lời tự khai về vi phạm, chưa phải bằng chứng vận hành độc lập; không có bằng chứng xác nhận skill bị sửa tay.
6. `tokens.total` của run chính thức không gồm các lượt thử và debug cũ; không có lịch sử đầy đủ để tính chi phí toàn quy trình. Trace chỉ phản ánh luồng chính, nên không dùng để suy ra nội bộ worker khi có delegation.


## 10. Kết luận

Trên ba task eval, skills-auto đạt trung bình `0,144444`, baseline `0,107407`, subagents `0,100673`, nhưng không run nào đọc skill hoặc gọi subagent. Cả ba điều kiện đạt `0/12` check quy ước eval; chênh lệch điểm không chứng minh tác động của skill hay phối hợp đa tác tử. Freeze và 18 artifact chính thức có thể đối chiếu, còn nguồn gốc curator và phép đo nhiễu trước/sau freeze của cùng bộ skill cuối chưa đủ bằng chứng. Bước tiếp theo là ghi model/limit và lượt kích hoạt skill trong từng run, rồi đo lặp độc lập cùng bộ skill đã đóng băng; đây là đề xuất, chưa thực hiện ở CP5.

## Phụ lục

- Ghi chép lịch sử trước CP2 (không còn đủ log/lệnh để kiểm chứng độc lập mọi lượt):
  1. `git fetch origin` và `git merge --ff-only origin/main` → cập nhật tới `ad29c55`.
  2. `.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-final` → **32 passed**.
  3. `.venv\Scripts\python.exe scripts\tour.py` → thành công.
  4. Kiểm tra model bằng endpoint người dùng cấu hình → trả `OK`; không đọc/sửa `.env` và không ghi endpoint hay khóa vào báo cáo.
  5. `baseline/data-learn` chạy thử 4 lần; các lượt đầu chạm recursion limit hoặc tạo đầu ra chưa đúng do sai khác shell Windows. Kết quả lưu cuối: 5/8, 63,934 token, không lỗi.
  6. `baseline/code-learn` → 2/10, 29,653 token; `baseline/logs-learn` → 1/9, 19,920 token.
  7. `subagents/code-learn` → 1/10, 75,817 token, GraphRecursionError ở limit 30; `subagents/data-learn` → 4/8, 57,684 token; `subagents/logs-learn` bị ngắt trước khi ghi record.
  8. `results/EXPERIMENT_NOTES.md` trong commit `hypotheses` ghi ba lượt curator đầu bị lỗi metadata, một lượt bổ sung sinh ba skill và tự nhận vượt giới hạn chạy lại. Không có log thô để xác định độc lập invocation, model call hoặc thứ tự lỗi/call.
- Windows/Git Bash thuộc giai đoạn thử cũ; các lượt bổ sung CP2–CP4 dùng Docker Linux/amd64. `.env` không tracked và không đưa giá trị vào báo cáo.
- Ghi chép cũ đếm chín lượt task đã bắt đầu trước CP2, kể cả một `subagents/logs-learn` bị ngắt; thêm một lượt CP2 thành mười theo ghi chép đó. Đây không phải tổng lịch sử đã kiểm chứng: có các lượt thử, backup và cohort sau này; không suy tổng chi phí API từ con số này.

### Trước freeze

Ghi chép trước freeze nói đã kiểm tra AST: các hằng số prompt có sẵn, render_trace, main, validate_skill và parse_skill_blocks giữ nguyên so với upstream; đồng thời nói chưa chạy hoặc phân tích eval. Đây là ghi chép quy trình, không chứng minh tuyệt đối chưa từng xem điểm eval. Lượt subagents code-learn chạy lại kết thúc GraphRecursionError (114,537 token); lượt subagents/logs-learn trước lần CP2 này gặp API timeout (7,625 token). Đây là các lỗi thực thi, không dùng để gán hành vi lỗi cho agent.

### CP2: chạy bổ sung

- Trước khi chạy lại `subagents/logs-learn`, lưu artifact cũ có `OpenAITimeoutError` (timestamp `2026-10-06T10:18:29.671229+00:00`, 125.8 giây) tại `results/failed-attempts/cp2-subagents-logs-learn-timeout-20261006/`; lý do: lỗi timeout API là lỗi hạ tầng. Chỉ chạy bổ sung tác vụ này một lần với `recursion_limit=40`.
- Đồng bộ `src/` và ba workspace learn từ repo máy chủ vào container Linux `codex-cp1`, xác minh SHA-256 các module CP1 trước chạy; chuyển `.env` vào container mà không in giá trị, rồi xóa bản container sau lần chạy. Lệnh tác vụ duy nhất lượt này: `python -m lab.runner --condition subagents --tasks logs-learn --recursion-limit 40 --results /tmp/cp2-results`. Kết quả `1/9`, `19,746` token, `11.5` giây, `subagent_calls=0`, `error=null`; `run.json` và `trace.md` đã đồng bộ về `results/subagents/logs-learn/` trên repo máy chủ. Không chạy lại baseline, API smoke test hay task nào khác.
- Sáu artifact learn dùng trong phân tích: `results/baseline/{code-learn,data-learn,logs-learn}/{run.json,trace.md}` và `results/subagents/{code-learn,data-learn,logs-learn}/{run.json,trace.md}`. Artifact timeout ban đầu được giữ riêng trong thư mục backup nêu trên; không đọc hay chạy artifact eval.

### CP3: kiểm tra bộ skill đã đóng băng

- Tag `freeze` đã có trước lượt CP3 này. Không gọi `python -m lab.curator`, không sửa skill, không tạo/di chuyển tag; số curator trước đó được report ghi là 4 lượt nhưng không có log thô để xác minh. Không chạy eval.
- Container ban đầu thiếu pytest/Deep Agents; tạo `/tmp/cp3-venv` trong container và cài editable từ `/lab`. Chạy `/tmp/cp3-venv/bin/python -m pytest tests/test_04_curator.py -o addopts= -q` → **2 passed**; `/tmp/cp3-venv/bin/python -m pytest tests/test_01_provided.py -o addopts= -q` → **15 passed**. SHA-256 các module và workspace learn trong container khớp repo máy chủ trước chạy.
- Các run learn cũ tại `results/skills-auto-dev/` và `results/skills-auto/` có `skills_sha256=2e16756003276761a6d85ba49d248033400488b016c6c852904dba1884780153`, không khớp bộ skill hiện tại; giữ nguyên, không tái sử dụng. Chạy mới một lần: `python -m lab.runner --condition skills-auto --tasks learn --recursion-limit 40 --results /tmp/cp3-final-results` (3 task, tổng `139,601` token). Artifact được đồng bộ về `results/skills-auto-dev-final-0612381b/{code-learn,data-learn,logs-learn}/{run.json,trace.md}`; mỗi `run.json` chứa hash bộ skill `0612381bb302045aceb44d137388f7332c9aecf83f58ff041690665f5faffaf0`. Đây là audit sau tag freeze, không phải lần dev trước freeze.
- Không chạy API smoke test. `.env` chỉ được chuyển tạm vào container để chạy ba task; đã xóa bản container sau đó, không in giá trị. Workspace nguồn trên repo máy chủ không bị sửa.

### Rà soát bằng chứng lịch sử CP3

- GUIDE 3.4 yêu cầu ba tác vụ learn với bộ skill trước freeze; GUIDE 4.2 phân biệt chúng với các run sau freeze cùng skill và khuyến nghị giữ artifact riêng. Ba run `results/skills-auto-dev/` có hash chung `2e16756003276761a6d85ba49d248033400488b016c6c852904dba1884780153`, không lỗi, không sửa skill và timestamp/duration cho thấy kết thúc trước freeze. Bundle tương ứng không còn trong Git hay bản sao lưu tìm được, nên không thể phục hồi hoặc kiểm tra lại hash qua `hash_skills`; không gán chúng cho bộ cuối.
- Commit `hypotheses` (`d0023cd3705815b5ede8f8357d8f74d4b2ac3357`, `2026-10-06T17:22:08+07:00`) chứa H1–H3 và thêm hai skill hiện tại; tag `freeze` (`9988c5c056b080947e6d3622e35da8d33ae18daf`, `2026-10-06T17:22:20+07:00`) theo sau 12 giây. Diff lịch sử không ghi nguồn tạo file; phần curator sinh skill chỉ được tự báo cáo, không có output curator độc lập được tìm thấy. Không có bằng chứng xác nhận sửa tay hay vi phạm.
- Bằng chứng mới trong repo là `results/EXPERIMENT_NOTES.md`, được thêm ở commit `hypotheses`: ghi ba lượt curator đầu không ghi skill vì metadata không hợp lệ, một lượt bổ sung tạo ba skill, và tự nhận vượt giới hạn hai lần chạy lại. Điều này giải thích khác nhau giữa ghi chú cũ về ba block bị loại và bốn lượt tổng. Không có log thô/prompt/output để phân biệt CLI invocation, model call, lỗi trước/sau call hay kiểm chứng số lần chạy lại; giữ kết luận là lời tự khai chưa được xác nhận độc lập. Không có bằng chứng xác nhận sửa tay hoặc dùng dữ liệu eval.
- Các run `results/skills-auto-dev-final-0612381b/` có hash cuối `0612381bb302045aceb44d137388f7332c9aecf83f58ff041690665f5faffaf0`, chạy sau freeze và không sửa skill. Chúng là cohort kiểm tra sau freeze, không phải lịch sử CP3.4 pre-freeze; không có dữ liệu CP3.4 pre-freeze cùng hash cuối để tính nhiễu cùng bộ skill.

| Tiêu chí CP3 liên quan | Trạng thái sau rà soát | Bằng chứng và giới hạn |
|---|---|---|
| GUIDE 3.3 / RUBRIC 4.1: curator tạo skill hợp lệ, không sửa tay | Có lời tự thuật; chưa xác nhận độc lập | `EXPERIMENT_NOTES.md` nói curator tạo ba skill; hai skill còn lại hợp lệ và được thêm ở commit `hypotheses`. Không có log/output gắn với các file để xác minh nguồn tạo hoặc lịch sử chỉnh sửa; cũng không có bằng chứng xác nhận sửa tay. |
| GUIDE 3.3: tối đa hai lần chạy lại | Tự khai là vượt giới hạn; không có log vận hành | Ghi chú nêu ba lượt metadata lỗi rồi một lượt bổ sung thành công và tự nhận vượt giới hạn. Không thể phân biệt độc lập invocation, model call, lỗi trước/sau call hoặc số lần chạy lại thực tế. |
| RUBRIC 4.2: đánh giá skill | Đã đánh giá hai skill hiện có; skill bị xóa chỉ có lý do tự thuật | Mục 6 nhận xét nội dung, tính đúng/sai, độ dài và description của hai skill còn lại. Ghi chú nói `test-suite-setup` bị xóa do pattern test sai; file không còn để đánh giá nội dung. |
| GUIDE 3.4: ba tác vụ learn trước freeze và kiểm tra sử dụng | Có run metadata/trace; không khôi phục được bộ skill | Ba run trước freeze cùng hash `2e167...`, `skills_read=0`, `skills_modified=false`; bundle thiếu nên không thể xác nhận hash bằng helper `hash_skills` hay gắn cohort này với hai skill cuối. |
| Không đưa dữ liệu eval vào curator | Chưa thể xác nhận từ prompt thực tế | `EXPERIMENT_NOTES.md` tự ghi không đưa eval vào; không tìm được prompt/log curator để kiểm tra độc lập. |

### CP4 và đối chiếu CP5

- Sau freeze, sáu baseline và năm subagents chính thức được tái sử dụng. `subagents/data-eval` cũ lỗi 429 được lưu ở `results/cp4-archive-20261006/subagents-data-eval-original/`; bản chính thức là một lượt mới, `1/9`, `error=null`. Ba learn hash cuối từ `results/skills-auto-dev-final-0612381b/` được sao byte vào `results/skills-auto/`. Ba eval skills-auto chạy một lần/task với limit 40; sáu run của cohort chính thức có cùng hash cuối, `skills_modified=false`, `skills_read=0`. Lệnh đầy đủ cho mọi lượt cũ không còn được xác minh, nên không trình bày chúng như nhật ký lệnh hoàn chỉnh.
- Các lệnh đối chiếu ngoại tuyến CP5 trước đó: `pytest -q -p no:cacheprovider` trong Docker Linux/Python 3.12.15 → 32 passed; `python -m lab.compare` → khớp nguyên `report/table.md`; `python scripts/check_breakdown.py` → khớp mục 7. Lượt rà soát tiếp theo dùng **container Docker mới** và sao nguyên byte `.git`, mã helper, script, `skills/auto/` và 12 artifact `results/skills-auto/`. SHA-256 từng file của hai `SKILL.md` và 12 artifact khớp máy chủ trước khi chạy; toàn bộ 38 file được kiểm tra trên máy chủ (hai skill và 36 artifact chính thức) không đổi hash sau khi chạy. `hash_skills` trong Linux trước và sau cấu hình là `0612381bb302045aceb44d137388f7332c9aecf83f58ff041690665f5faffaf0`, trùng sáu `run.json`.
- Không có `.gitattributes`. Máy chủ dùng `core.autocrlf=true` từ Git system config; Git index lưu LF, file skill làm việc lưu CRLF. Container mới ban đầu không có `core.autocrlf`: `verify_freeze.py` báo `FAIL: skills/ differs from the freeze tag` và `checked 6 runs of skill conditions: 1 problem(s)`; sáu phép so hash không báo lỗi. Đặt `git config --local core.autocrlf true` **chỉ trong `/lab/.git/config` của bản sao container**, khớp máy chủ, rồi chạy nguyên `python scripts/verify_freeze.py` → `checked 6 runs of skill conditions: OK` (exit 0). Cấu hình này cho phép Git kiểm tra đúng CRLF của worktree so với LF của index; không bỏ qua diff hoặc thay nội dung. Không sửa skill, artifact, timestamp, script, tag, repo máy chủ hay lịch sử Git.

### CP6c: red team curator ngoại tuyến

- Thí nghiệm dùng `report/curator_redteam.py`, dữ liệu learn tổng hợp trong thư mục tạm, fake model có kịch bản cố định và luồng thật `curate_skills` → `parse_skill_blocks` → `validate_skill` → ghi `SKILL.md`. Ca marker trực tiếp dùng ID `code-eval` từ `eval_markers()` trên task skeleton tổng hợp; không đọc instruction, workspace, đáp án hay `check.py` của task lab để dựng ca. Sentinel `SENTINEL-ORCHID-73` là dữ liệu giả.
- Cùng 6 ca tấn công được chạy trước/sau bộ chuẩn hóa Unicode trong script. Control lành tính được giữ cả hai lượt. Validator gốc chặn traversal và marker trực tiếp (2/6), nhưng nhận hai biến thể Unicode cùng ca sentinel và feedback độc hại (4/6 được ghi). Guard chặn traversal, marker trực tiếp và hai biến thể (4/6); sentinel và yêu cầu đọc dữ liệu tổng quát vẫn được ghi (2/6). Cả hai giữ control, false block `0`, ghi ngoài thư mục đích `0`.

| Ca | Validator/curator gốc | Guard trong script | Ghi ngoài đích |
|---|---|---|---:|
| Control lành tính | Giữ | Giữ | 0 |
| Tên `../outside` | Chặn | Chặn | 0 |
| Marker `code-eval` trực tiếp | Chặn | Chặn | 0 |
| Marker có dấu gạch Unicode hoặc zero-width | Chấp nhận cả 2 | Chặn cả 2 | 0 |
| Sentinel/đọc dữ liệu eval nhưng không có marker | Chấp nhận | Chấp nhận | 0 |
| Feedback learn yêu cầu bỏ qua quy tắc/đọc dữ liệu | Prompt nhận feedback; skill giả được ghi | Prompt vẫn nhận; skill giả vẫn được ghi | 0 |

- `parse_skill_blocks` nhận diện đủ 7 block, kể cả block có tên `../outside`; sau đó `validate_skill` loại tên traversal và marker trực tiếp. Trace cho thấy hai cơ chế: skill chứa `code‑eval` với U+2011 vượt validator gốc và được ghi, nhưng guard chuẩn hóa thành `code-eval` rồi loại; prompt curator đưa nguyên feedback tổng hợp “IGNORE prior rules…” vào phần failed-check detail, và fake model trả đầu ra chứa sentinel mà validator chấp nhận. Fake model chỉ chứng minh dữ liệu đi vào prompt và luồng parser/ghi chấp nhận đầu ra scripted; không chứng minh LLM thật bị thao túng.
- Hai skill chính thức hợp lệ về định dạng và đóng băng đúng hash, nhưng sáu run skills-auto chính thức đều `skills_read=0`; hợp lệ cú pháp không chứng minh an toàn ngữ nghĩa. Thí nghiệm tổng hợp không kết luận hai skill thật có tấn công hay rò rỉ. Nguồn gốc curator của skill vẫn chỉ có lời tự thuật ở `EXPERIMENT_NOTES.md`, không có log độc lập.
- Biện pháp đã chạy là chuẩn hóa NFKC, Unicode dash, ký tự format và escape `\\uXXXX` trước khi so marker, chỉ trong script red team. Nó chặn các biến thể tên đã thử, không chặn ý nghĩa yêu cầu đọc dữ liệu hoặc sentinel không chứa marker. Bước tiếp theo đề xuất là kiểm tra nội dung theo chính sách nguồn dữ liệu và đánh giá output trong sandbox; chưa triển khai.
- Tái lập trong Linux: `python report/curator_redteam.py --output-dir results/extension-curator-redteam`. Self-check trong script đạt; không gọi API, chi phí API bằng 0. Kết quả riêng: `results/extension-curator-redteam/{results.json,trace.md,README.md}`. `results/extension-redteam/` cũ không bị ghi đè.
- Sau đồng bộ raw bytes vào container Linux, cấu hình `core.autocrlf=true` trong `.git/config` của container rồi chạy `python scripts/verify_freeze.py` → `checked 6 runs of skill conditions: OK` (exit 0). `hash_skills` trước/sau đều `0612381bb302045aceb44d137388f7332c9aecf83f58ff041690665f5faffaf0`; SHA-256 từng file của 38 skill/artifact chính thức trước và sau khớp.

| Tiêu chí thưởng CP6 | Bằng chứng trong lượt này |
|---|---|
| Thiết kế tách khỏi kết quả chính | 7 ca synthetic/fake-model; output ở thư mục mở rộng riêng |
| Số liệu so sánh | Cùng 6 tấn công: blocked 2/6 → 4/6; control 1/1; false block 0; ghi ngoài đích 0 |
| Cơ chế theo trace | Biến thể Unicode qua validator và feedback learn đi nguyên vào prompt |
| Hạn chế/bước tiếp theo | Fake model, sentinel tổng hợp, semantic requests còn lọt; đề xuất kiểm tra chính sách dữ liệu trong sandbox |
| Mã/tái lập | Script có self-check, README, lệnh Linux; không gọi API |

- Các hạng mục CP6c trên có artifact kiểm tra được; không tự quy đổi thành +5. RUBRIC chỉ tính thưởng nếu hạng mục 1–6 hoàn tất, trong khi một số bằng chứng CP3 vẫn là tự thuật chưa được xác nhận độc lập.

### Cách tái lập và nguồn

- Trên Linux/amd64 hoặc Docker với Python ≥3.11, dùng bản clone có cả Git tag `freeze`, `results/` và `skills/auto/`; cài `pip install -e .`, rồi chạy `pytest`, `python scripts/verify_freeze.py`, `python -m lab.compare` (đối chiếu output với `report/table.md`) và `python scripts/check_breakdown.py`. Trên máy này ổ E: không mount vào Docker nên dùng `docker cp` để đưa repo vào container; phải bảo toàn **raw bytes** của skill và artifact. Khi sao worktree Windows có CRLF cùng `.git` vào Linux, đặt `git config --local core.autocrlf true` **trong bản sao container** trước khi chạy `verify_freeze.py`, vì repo máy chủ cũng dùng cấu hình đó. Với clone Linux mới có worktree LF, giữ cấu hình Git phù hợp worktree của clone; không tự chuyển xuống dòng skill đã dùng trong run. Đây là tái lập bảng/check từ artifact hiện có, không gọi API.
- Muốn tạo kết quả thí nghiệm *mới* trong môi trường có khóa API và model hỗ trợ tool calling, dùng lệnh của GUIDE: `python -m lab.runner --condition baseline --tasks eval`, `python -m lab.runner --condition subagents --tasks eval`, `python -m lab.runner --condition skills-auto --tasks all` với `--recursion-limit 40` nếu muốn đối chiếu cấu hình lượt mới. Dùng `--results` khác để giữ artifact cũ; kết quả mới có thể khác và không sửa lịch sử của báo cáo này. CP5 không chạy những lệnh đó.
- Tài liệu dùng để giải thích cơ chế, đã mở kiểm tra ở CP5: [Deep Agents Subagents](https://docs.langchain.com/oss/python/deepagents/subagents) về delegation/context; [Deep Agents Skills](https://docs.langchain.com/oss/python/deepagents/skills) về nạp skill. Hai nguồn này đã được dẫn trong giả thuyết trước freeze; việc đọc lại ở CP5 chỉ phục vụ thảo luận, không thêm căn cứ hồi tố hoặc sửa H1–H3. Tài liệu nội bộ: `README.md` mục 2, `GUIDE.md` Phần 3–5, `RUBRIC.md` mục 4–6, `REPORT_TEMPLATE.md`.
- CP6c được chạy riêng như mô tả ở phụ lục; không thay đổi 18 cặp artifact chính thức hoặc hai skill đóng băng.
