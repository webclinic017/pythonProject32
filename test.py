from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule


if __name__ == '__main__':
    # 生成示例二维数组
    data = [[1, 2, 3], [4, 5, 6], [7, 20, 9]]

    # 创建 Excel 文件并选中当前工作表
    wb = Workbook()
    ws = wb.active

    # 将二维数组写入 Excel 单元格
    for row in data:
        ws.append(row)

    # 使用颜色刻度条设置条件格式，根据数值大小对背景颜色进行渐变
    # ff0000红色， 00ff00绿色
    grad_rule = ColorScaleRule(start_type='min', start_color='ffffff', end_type='max', end_color='00FF00')
    ws.conditional_formatting.add('A1:C3', grad_rule)

    # 保存 Excel 文件
    wb.save('example.xlsx')

