from dataclasses import dataclass
from typing import Dict, List

# 排班表数据结构定义
@dataclass
class ScheduleShift:
    """排班班次"""
    position: str  # 岗位，如 "MR1", "MR2" 等
    time_range: str  # 时间范围，如 "07:30-13:00"
    assignments: Dict[str, str]  # 日期到人员姓名的映射

@dataclass
class ScheduleTable:
    """排班表"""
    title: str  # 表标题，如 "MRI上午", "MRI下午", "MRI晚班", "周末班"
    shifts: List[ScheduleShift]  # 班次列表
    dates: List[str]  # 日期列表，如 ["8月4日", "8月5日", ...]

@dataclass
class ScheduleData:
    """完整的排班数据"""
    week: str  # 周次，如 "2024-32"
    tables: List[ScheduleTable]  # 排班表列表

def get_mock_schedule_data(week: str) -> ScheduleData:
    """获取mock排班数据"""
    
    # MRI上午班次
    mri_morning_shifts = [
        ScheduleShift("MR1", "07:30-13:00", {
            "8月4日": "张三", "8月5日": "李四", "8月6日": "王五", "8月7日": "赵六", "8月8日": "钱七"
        }),
        ScheduleShift("MR2", "07:30-13:00", {
            "8月4日": "孙八", "8月5日": "周九", "8月6日": "吴十", "8月7日": "郑十一", "8月8日": "王十二"
        }),
        ScheduleShift("MR3", "07:30-13:00", {
            "8月4日": "孙八", "8月5日": "陈十四", "8月6日": "褚十五", "8月7日": "孙八", "8月8日": "蒋十七"
        }),
        ScheduleShift("MR4", "07:30-13:00", {
            "8月4日": "沈十八", "8月5日": "韩十九", "8月6日": "杨二十", "8月7日": "朱二一", "8月8日": "秦二二"
        }),
        ScheduleShift("MR5", "07:30-13:00", {
            "8月4日": "尤二三", "8月5日": "许二四", "8月6日": "何二五", "8月7日": "吕二六", "8月8日": "施二七"
        }),
        ScheduleShift("MR6", "07:30-13:00", {
            "8月4日": "张二八", "8月5日": "孔二九", "8月6日": "曹三十", "8月7日": "严三一", "8月8日": "华三二"
        }),
        ScheduleShift("MR7", "07:30-13:00", {
            "8月4日": "金三三", "8月5日": "魏三四", "8月6日": "孙八", "8月7日": "姜三六", "8月8日": "戚三七"
        }),
        ScheduleShift("MR8", "07:30-13:00", {
            "8月4日": "谢三八", "8月5日": "孙八", "8月6日": "喻四十", "8月7日": "柏四一", "8月8日": "水四二"
        }),
        ScheduleShift("MR9", "07:30-13:00", {
            "8月4日": "窦四三", "8月5日": "章四四", "8月6日": "云四五", "8月7日": "苏四六", "8月8日": "潘四七"
        }),
        ScheduleShift("MR10", "07:30-13:00", {
            "8月4日": "葛四八", "8月5日": "奚四九", "8月6日": "孙八", "8月7日": "彭五一", "8月8日": "郎五二"
        }),
        ScheduleShift("MR11", "07:30-13:00", {
            "8月4日": "鲁五三", "8月5日": "孙八", "8月6日": "昌五五", "8月7日": "马五六", "8月8日": "苗五七"
        }),
        ScheduleShift("MR12", "07:30-13:00", {
            "8月4日": "孙八", "8月5日": "花五九", "8月6日": "孙八", "8月7日": "俞六一", "8月8日": "任六二"
        }),
        ScheduleShift("MR13", "07:30-13:00", {
            "8月4日": "袁六三", "8月5日": "柳六四", "8月6日": "酆六五", "8月7日": "鲍六六", "8月8日": "史六七"
        })
    ]
    
    # MRI下午班次
    mri_afternoon_shifts = [
        ScheduleShift("MR1", "13:00-18:30", {
            "8月4日": "唐六八", "8月5日": "费六九", "8月6日": "廉七十", "8月7日": "岑七一", "8月8日": "薛七二"
        }),
        ScheduleShift("MR2", "13:00-18:30", {
            "8月4日": "雷七三", "8月5日": "贺七四", "8月6日": "倪七五", "8月7日": "汤七六", "8月8日": "滕七七"
        }),
        ScheduleShift("MR3", "13:00-18:30", {
            "8月4日": "殷七八", "8月5日": "罗七九", "8月6日": "毕八十", "8月7日": "郝八一", "8月8日": "邬八二"
        }),
        ScheduleShift("MR4", "13:00-18:30", {
            "8月4日": "安八三", "8月5日": "孙八", "8月6日": "乐八五", "8月7日": "于八六", "8月8日": "时八七"
        }),
        ScheduleShift("MR5", "13:00-18:30", {
            "8月4日": "傅八八", "8月5日": "皮八九", "8月6日": "卞九十", "8月7日": "齐九一", "8月8日": "康九二"
        }),
        ScheduleShift("MR6", "13:00-18:30", {
            "8月4日": "伍九三", "8月5日": "余九四", "8月6日": "元九五", "8月7日": "卜九六", "8月8日": "顾九七"
        }),
        ScheduleShift("MR7", "13:00-18:30", {
            "8月4日": "孟九八", "8月5日": "平九九", "8月6日": "黄一百", "8月7日": "孙八", "8月8日": "穆百二"
        }),
        ScheduleShift("MR8", "13:00-18:30", {
            "8月4日": "萧百三", "8月5日": "孙八", "8月6日": "姚百五", "8月7日": "邵百六", "8月8日": "湛百七"
        }),
        ScheduleShift("MR9", "13:00-18:30", {
            "8月4日": "汪百八", "8月5日": "祁百九", "8月6日": "毛百十", "8月7日": "禹百十一", "8月8日": "狄百十二"
        }),
        ScheduleShift("MR10", "13:00-18:30", {
            "8月4日": "米百十三", "8月5日": "贝百十四", "8月6日": "明百十五", "8月7日": "臧百十六", "8月8日": "计百十七"
        }),
        ScheduleShift("MR11", "13:00-18:30", {
            "8月4日": "伏百十八", "8月5日": "成百十九", "8月6日": "戴百二十", "8月7日": "谈百二一", "8月8日": "宋百二二"
        }),
        ScheduleShift("MR12", "13:00-18:30", {
            "8月4日": "茅百二三", "8月5日": "庞百二四", "8月6日": "熊百二五", "8月7日": "纪百二六", "8月8日": "舒百二七"
        }),
        ScheduleShift("MR13", "13:00-18:30", {
            "8月4日": "屈百二八", "8月5日": "项百二九", "8月6日": "祝百三十", "8月7日": "董百三一", "8月8日": "梁百三二"
        })
    ]
    
    # MRI晚班班次
    mri_evening_shifts = [
        ScheduleShift("MR1", "18:30-23:00", {
            "8月4日": "杜百三三", "8月5日": "阮百三四", "8月6日": "蓝百三五", "8月7日": "闵百三六", "8月8日": "席百三七"
        }),
        ScheduleShift("MR2", "18:30-23:00", {
            "8月4日": "季百三八", "8月5日": "孙八", "8月6日": "强百四十", "8月7日": "贾百四一", "8月8日": "路百四二"
        }),
        ScheduleShift("MR3", "18:30-23:00", {
            "8月4日": "娄百四三", "8月5日": "危百四四", "8月6日": "江百四五", "8月7日": "童百四六", "8月8日": "颜百四七"
        }),
        ScheduleShift("MR4", "18:30-23:00", {
            "8月4日": "郭百四八", "8月5日": "梅百四九", "8月6日": "孙八五十", "8月7日": "林百五一", "8月8日": "刁百五二"
        }),
        ScheduleShift("MR5", "18:30-23:00", {
            "8月4日": "钟百五三", "8月5日": "徐百五四", "8月6日": "邱百五五", "8月7日": "骆百五六", "8月8日": "高百五七"
        }),
        ScheduleShift("MR6", "18:30-23:00", {
            "8月4日": "夏百五八", "8月5日": "蔡百五九", "8月6日": "田百六十", "8月7日": "樊百六一", "8月8日": "胡百六二"
        }),
        ScheduleShift("MR7", "18:30-23:00", {
            "8月4日": "凌百六三", "8月5日": "霍百六四", "8月6日": "虞百六五", "8月7日": "万百六六", "8月8日": "支百六七"
        }),
        ScheduleShift("MR8", "18:30-23:00", {
            "8月4日": "柯百六八", "8月5日": "昝百六九", "8月6日": "管百七十", "8月7日": "卢百七一", "8月8日": "莫百七二"
        }),
        ScheduleShift("MR9", "18:30-23:00", {
            "8月4日": "经百七三", "8月5日": "房百七四", "8月6日": "裘百七五", "8月7日": "缪百七六", "8月8日": "干百七七"
        }),
        ScheduleShift("MR10", "18:30-23:00", {
            "8月4日": "解百七八", "8月5日": "应百七九", "8月6日": "孙八八十", "8月7日": "丁百八一", "8月8日": "宣百八二"
        }),
        ScheduleShift("MR11", "18:30-23:00", {
            "8月4日": "贲百八三", "8月5日": "邓百八四", "8月6日": "郁百八五", "8月7日": "单百八六", "8月8日": "杭百八七"
        })
    ]
    
    # 周末班班次
    weekend_shifts = [
        ScheduleShift("MR1", "07:30-13:00", {
            "8月9日": "洪百八八", "8月10日": "包百八九"
        }),
        ScheduleShift("MR2", "07:30-13:00", {
            "8月9日": "诸百九十", "8月10日": "左百九一"
        }),
        ScheduleShift("MR3", "07:30-13:00", {
            "8月9日": "石百九二", "8月10日": "崔百九三"
        }),
        ScheduleShift("MR4", "07:30-13:00", {
            "8月9日": "吉百九四", "8月10日": "钮百九五"
        }),
        ScheduleShift("MR5", "07:30-13:00", {
            "8月9日": "龚百孙八", "8月10日": "程百九七"
        }),
        ScheduleShift("MR6", "07:30-13:00", {
            "8月9日": "嵇百九八", "8月10日": "邢百九九"
        }),
        ScheduleShift("MR7", "07:30-13:00", {
            "8月9日": "滑二百", "8月10日": "裴二百一"
        }),
        ScheduleShift("MR8", "07:30-13:00", {
            "8月9日": "陆二百二", "8月10日": "荣二百三"
        }),
        ScheduleShift("MR9", "07:30-13:00", {
            "8月9日": "翁二百四", "8月10日": "荀二百五"
        }),
        ScheduleShift("MR10", "07:30-13:00", {
            "8月9日": "孙八", "8月10日": "於二百七"
        }),
        ScheduleShift("MR11", "07:30-13:00", {
            "8月9日": "惠二百八", "8月10日": "甄二百九"
        }),
        ScheduleShift("MR12", "07:30-13:00", {
            "8月9日": "曲二百十", "8月10日": "家二百十一"
        }),
        ScheduleShift("晚班行政班", "18:30-23:00", {
            "8月9日": "封二百十二", "8月10日": "芮二百十三"
        }),
        ScheduleShift("补休周末班", "全天", {
            "8月9日": "羿二百十四", "8月10日": "储二百十五"
        })
    ]
    
    # 创建排班表
    mri_morning_table = ScheduleTable("MRI上午", mri_morning_shifts, ["8月4日", "8月5日", "8月6日", "8月7日", "8月8日"])
    mri_afternoon_table = ScheduleTable("MRI下午", mri_afternoon_shifts, ["8月4日", "8月5日", "8月6日", "8月7日", "8月8日"])
    mri_evening_table = ScheduleTable("MRI晚班", mri_evening_shifts, ["8月4日", "8月5日", "8月6日", "8月7日", "8月8日"])
    weekend_table = ScheduleTable("周末班", weekend_shifts, ["8月9日", "8月10日"])
    
    return ScheduleData(week, [mri_morning_table, mri_afternoon_table, mri_evening_table, weekend_table]) 


def read_schedule_from_csv(week: str) -> ScheduleData:
    """从CSV文件读取排班数据"""
    import csv
    import os
    from pathlib import Path
    
    # 构建CSV文件路径
    base_dir = Path(__file__).resolve().parents[1]
    csv_path = base_dir / "data" / "schedules" / f"{week}.csv"
    
    if not csv_path.exists():
        # 如果CSV文件不存在，返回mock数据
        return get_mock_schedule_data(week)
    
    # 存储解析后的数据
    table_data = {}  # {table_title: {position: {date: staff_name}}}
    dates = set()
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                table_title = row['table_title']
                position = row['position']
                time_range = row['time_range']
                date = row['date']
                staff_name = row['staff_name']
                
                # 收集所有日期
                dates.add(date)
                
                # 初始化数据结构
                if table_title not in table_data:
                    table_data[table_title] = {}
                
                if position not in table_data[table_title]:
                    table_data[table_title][position] = {
                        'time_range': time_range,
                        'assignments': {}
                    }
                
                # 添加排班信息
                table_data[table_title][position]['assignments'][date] = staff_name
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        # 如果读取失败，返回mock数据
        return get_mock_schedule_data(week)
    
    # 转换为ScheduleData格式
    tables = []
    dates_list = sorted(list(dates))
    
    for table_title, positions in table_data.items():
        shifts = []
        for position, data in positions.items():
            shift = ScheduleShift(
                position=position,
                time_range=data['time_range'],
                assignments=data['assignments']
            )
            shifts.append(shift)
        
        table = ScheduleTable(
            title=table_title,
            shifts=shifts,
            dates=dates_list
        )
        tables.append(table)
    
    return ScheduleData(week=week, tables=tables)


def get_schedule_data(week: str) -> ScheduleData:
    """获取排班数据，优先从数据库读取手动填写的数据，然后尝试CSV，最后返回mock数据"""
    # 首先尝试从数据库读取手动填写的数据
    try:
        from app.main import get_manual_schedule_data
        manual_data = get_manual_schedule_data(week)
        if manual_data:
            print(f"成功从数据库获取手动排班数据：{week}")
            return manual_data
    except Exception as e:
        print(f"从数据库读取手动排班数据失败: {e}")
    
    # 然后尝试从CSV读取
    try:
        return read_schedule_from_csv(week)
    except Exception as e:
        print(f"Failed to read CSV, falling back to mock data: {e}")
        return get_mock_schedule_data(week) 