# Nhật ký chạy và giới hạn

Các run.json hiện có là record của lượt gần nhất; lượt chạy lại cùng đường dẫn ghi đè record trước. Không dùng các lỗi hạ tầng như bằng chứng về chất lượng tác tử.

- Baseline data-learn: các lượt debug lần lượt 364,010 token (recursion 60), 61,716 token (recursion 20), 19,237 token (script Windows cmd không hoàn thành yêu cầu), rồi 63,934 token với Git Bash (5/8, không lỗi). Các lượt debug không có trong trung bình so sánh chính.
- Subagents code-learn: 75,817 token, recursion 30; chạy lại 114,537 token, recursion 40. Cả hai chạm giới hạn graph. Bản lưu gần nhất giữ trace trung gian; các tool call không bị mất khi lỗi.
- Subagents logs-learn: hai lượt dài bị ngắt, chưa ghi run.json; một lượt API timeout 45 giây ghi được 7,625 token và lỗi. Thử lại timeout 120 giây, max_retries=0.
- Curator: 3 lượt đầu không ghi skill do metadata không hợp lệ; prompt được sửa và một lượt bổ sung sinh 3 skill. Đây là vượt giới hạn 2 lần thử lại của GUIDE; được ghi rõ, không che giấu. Xóa toàn bộ test-suite-setup do pattern test sai, không sửa nội dung hai skill giữ lại.
- Không đưa dữ liệu hoặc điểm eval vào curator. Tập eval chỉ chạy sau commit hypotheses và tag freeze. .env không bị chỉnh sửa.
