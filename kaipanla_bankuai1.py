# -*- coding: utf-8 -*-
import streamlit as st
import requests
import datetime
import pandas as pd
import json
import akshare as ak
import plotly.graph_objects as go
import os

# ---------------------- 配置区域 ----------------------

# 设置页面布局
st.set_page_config(layout="wide", page_title="精选板块分析", page_icon="🚀")


# ---------------------- 数据获取函数 ----------------------

def get_sector_data(date, k, zs_type):
    """
    获取板块排名数据
    """
    url1 = "https://apphq.longhuvip.com/w1/api/index.php"
    url2 = "https://apphis.longhuvip.com/w1/api/index.php"

    headers = {
        "Host": "apphis.longhuvip.com" if k == 1 else "apphq.longhuvip.com",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "lhb/5.17.9 (com.kaipanla.www; build:0; iOS 16.6.0) Alamofire/4.9.1",
        "Accept-Language": "zh-Hans-CN;q=1.0",
        "Accept-Encoding": "gzip;q=1.0, compress;q=0.5"
    }

    params = {
        "Date": date if k == 1 else datetime.date.today().strftime("%Y-%m-%d"),
        "Index": "0",
        "Order": "1",
        "PhoneOSNew": "2",
        "Type": "1",
        "VerSion": "5.17.0.9",
        "ZSType": str(zs_type),
        "a": "RealRankingInfo",
        "apiv": "w38",
        "c": "ZhiShuRanking",
        "st": "50"
    }

    url = url1 if k == 0 else url2
    try:
        response = requests.post(url, headers=headers, data=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "list" in data and data["list"]:
                sector_list = []
                for item in data["list"]:
                    # 确保数据长度足够
                    if len(item) >= 4:
                        sector_list.append({
                            "代码": item[0],
                            "名称": item[1],
                            "强度": item[2],
                            "涨幅%": item[3]
                        })
                return sector_list
    except Exception as e:
        st.error(f"获取板块数据出错：{str(e)}")
    return []


def get_stock_data(sector_code, date, k):
    """
    获取历史成分股数据 (长横接口)
    """
    url1 = "https://apphq.longhuvip.com/w1/api/index.php"
    url2 = "https://apphis.longhuvip.com/w1/api/index.php"
    headers = {
        "Host": "apphis.longhuvip.com" if k == 1 else "apphq.longhuvip.com",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "lhb/5.17.9 (com.kaipanla.www; build:0; iOS 16.6.0) Alamofire/4.9.1",
        "Accept-Language": "zh-Hans-CN;q=1.0",
        "Accept-Encoding": "gzip;q=1.0, compress;q=0.5"
    }
    params = {
        "PlateID": sector_code,
        "Date": date if k == 1 else datetime.date.today().strftime("%Y-%m-%d"),
        "Index": "0",
        "Order": "1",
        "PhoneOSNew": "2",
        "Type": "6",
        "VerSion": "5.17.0.9",
        "a": "ZhiShuStockList_W8",
        "apiv": "w38",
        "c": "ZhiShuRanking",
        "st": "1000",
        "Token": "eda418788f6e7eeff78b6522d586afb"
    }
    url = url1 if k == 0 else url2
    try:
        response = requests.post(url, headers=headers, data=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "list" in data and data["list"]:
                stock_list = []
                for item in data["list"]:
                    if len(item) >= 25:
                        stock_list.append({
                            "代码": item[0],
                            "名称": item[1],
                            "涨幅%": item[6],
                            "价格": item[5],
                            "成交额": str(int(float(item[7]) / 10000)) + '万',
                            '实际流通值': str(int(float(item[10]) / 100000000)) + '亿',
                            "板块": item[4],
                            "连板": item[23],
                            "龙头": item[24],
                        })
                return stock_list
    except Exception as e:
        print(f"历史数据接口请求出错: {e}")
    return []


def get_stock_data_tencent(stock_codes):
    """
    通过腾讯接口获取实时行情 (支持批量分次请求)
    """
    if not stock_codes:
        return []

    all_results = []
    # 腾讯接口每次请求建议不超过 60 个股票，防止 URL 过长
    batch_size = 50

    for i in range(0, len(stock_codes), batch_size):
        batch_codes = stock_codes[i:i + batch_size]
        url = f"https://web.sqt.gtimg.cn/q={','.join(batch_codes)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://gu.qq.com/'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            text = response.text
            lines = text.strip().split(';')

            for line in lines:
                if not line or '"' not in line:
                    continue

                content = line.split('~')
                # 腾讯数据位比较多，确保长度足够
                if len(content) > 37:
                    all_results.append({
                        "代码": content[2],  # v_code (纯数字代码)
                        "名称": content[1],  # v_name
                        "价格": float(content[3]),
                        "涨跌额": float(content[31]),
                        "涨幅%": float(content[32]),
                        "最高": float(content[33]),
                        "最低": float(content[34]),
                        "成交量(手)": float(content[36]),
                        "成交额": float(content[37])
                    })
        except Exception as e:
            st.warning(f"腾讯接口部分数据请求出错: {e}")

    return all_results


@st.cache_data(ttl=3600)  # 缓存1小时
def get_son_plate_info(plate_id):
    url = "https://apphwshhq.longhuvip.com/w1/api/index.php"
    params = {
        "DEnd": "", "Date": "", "PhoneOSNew": "2", "PlateID": plate_id,
        "VerSion": "5.17.0.9", "a": "SonPlate_Info", "apiv": "w38", "c": "ZhiShuRanking"
    }
    headers = {
        "Host": "apphwshhq.longhuvip.com", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Connection": "keep-alive", "Accept": "*/*",
        "User-Agent": "lhb/5.17.9 (com.kaipanla.www; build:0; iOS 16.6.0) Alamofire/4.9.1",
        "Accept-Language": "zh-Hans-CN;q=1.0", "Accept-Encoding": "gzip;q=1.0, compress;q=0.5"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("errcode") == "0" and "List" in data:
                return [{"代码": i[0], "名称": i[1], "强度": i[2]} for i in data["List"] if len(i) >= 3]
    except:
        pass
    return []


@st.cache_data(ttl=600)  # 缓存10分钟
def get_sector_kline_data(sector_code):
    url = "https://apphis.longhuvip.com/w1/api/index.php"
    headers = {
        "Host": "apphis.longhuvip.com", "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Connection": "keep-alive", "Accept": "*/*",
        "User-Agent": "lhb/5.17.9 (com.kaipanla.www; build:0; iOS 16.6.0) Alamofire/4.9.1",
        "Accept-Language": "zh-Hans-CN;q=1.0", "Accept-Encoding": "gzip;q=1.0, compress;q=0.5"
    }
    form_data = {
        'Index': '0', 'PhoneOSNew': '2', 'StockID': sector_code, 'VerSion': '5.21.0.1',
        'a': 'GetPlateKLineDay', 'apiv': 'w42', 'c': 'ZhiShuKLine', 'st': '600',
    }
    try:
        response = requests.post(url, data=form_data, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'x' in result and 'y' in result:
                df = pd.DataFrame(result['y'], columns=['open', 'close', 'high', 'low'])
                df['date'] = pd.to_datetime(result['x'], format='%Y%m%d')
                df['volume'] = result.get('vol', [0] * len(df))
                df.sort_values('date', inplace=True)
                return df
    except:
        pass
    return None


def is_trading_day(date):
    try:
        trade_date_df = ak.tool_trade_date_hist_sina()
        return date.strftime("%Y-%m-%d") in trade_date_df["trade_date"].astype(str).values
    except:
        # 如果akshare请求失败，默认返回True，避免阻断流程
        return True


def get_previous_trading_day(from_date):
    """获取 from_date 的前一个交易日"""
    d = from_date
    for _ in range(10):
        d = d - datetime.timedelta(days=1)
        if is_trading_day(d):
            return d
    return from_date


def is_before_market_open():
    """当前时间是否在当日 9:15 之前（此时当日数据尚未产生）"""
    now = datetime.datetime.now()
    return now.hour < 9 or (now.hour == 9 and now.minute < 15)


# ---------------------- 辅助逻辑 ----------------------

def format_stock_code(code_6_digits):
    s_code = str(code_6_digits).zfill(6)
    if s_code.startswith('6') or s_code.startswith('9'):
        return f"sh{s_code}"
    elif s_code.startswith('0') or s_code.startswith('2') or s_code.startswith('3'):
        return f"sz{s_code}"
    else:
        return f"sh{s_code}"


@st.cache_data
def load_sector_map():
    csv_path = "stock_sector_data.csv"
    if not os.path.exists(csv_path):
        return None

    try:
        df = pd.read_csv(csv_path, dtype=str)
        df.columns = [c.strip() for c in df.columns]
        if '板块code' in df.columns:
            df['板块code'] = df['板块code'].str.strip()
        if '股票代码' in df.columns:
            df['股票代码'] = df['股票代码'].str.strip().str.zfill(6)
        return df
    except Exception as e:
        st.error(f"读取 CSV 文件出错: {e}")
        return None


# ---------------------- 页面布局 ----------------------

def app():
    st.title("🚀 精选板块与成分股分析")

    # 1. 日期选择逻辑
    today = datetime.date.today()
    date_range = [today - datetime.timedelta(days=i) for i in range(30)]
    formatted_date_range = [d.strftime("%Y-%m-%d") for d in date_range]

    with st.sidebar:
        st.subheader("设置")
        selected_date = st.selectbox("选择日期", formatted_date_range, index=0)
        selected_date_obj = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()

        if is_trading_day(selected_date_obj):
            st.success(f"📅 {selected_date} (交易日)")
        else:
            st.warning(f"⚠️ {selected_date} (非交易日)")
            st.info("非交易日可能无历史数据，是否继续？")
            if not st.button("继续加载"):
                st.stop()

        # 若选的是“今天”且当前在 9:15 之前，当日数据尚未产生，改为使用前一交易日
        if selected_date == today.strftime("%Y-%m-%d") and is_before_market_open():
            effective_date_obj = get_previous_trading_day(today)
            effective_date = effective_date_obj.strftime("%Y-%m-%d")
            k = 1  # 走历史接口
            st.info(f"⏰ 当前未到 9:15，展示 **前一交易日** 数据：{effective_date}")
        else:
            effective_date = selected_date
            k = 0 if selected_date == today.strftime("%Y-%m-%d") else 1

    # 2. 标签页
    tab1, tab2, tab3 = st.tabs(["📈 概念", "🏢 行业", "📍 地区"])
    tabs_map = {tab1: 7, tab2: 4, tab3: 6}

    for tab in [tab1, tab2, tab3]:
        with tab:
            zs_type = tabs_map[tab]

            # 3. 获取板块列表
            with st.spinner(f"正在加载 {tab.title} 板块排名..."):
                sector_data = get_sector_data(effective_date, k, zs_type)

            if not sector_data:
                st.warning("未获取到板块数据，请检查网络或更换日期。")
                continue

            df_sectors = pd.DataFrame(sector_data)
            # 创建代码到名称的映射，用于后续显示
            code_to_name = dict(zip(df_sectors['代码'], df_sectors['名称']))

            # 4. 左右分栏
            col_list, col_detail = st.columns([4, 6])

            with col_list:
                st.subheader("板块排名")

                # 显示排名表格
                st.dataframe(
                    df_sectors,
                    use_container_width=True,
                    height=600,
                    hide_index=True,
                    column_config={
                        "代码": st.column_config.TextColumn("代码", width="small"),
                        "名称": st.column_config.TextColumn("名称", width="medium"),
                        "强度": st.column_config.NumberColumn("强度", format="%.2f", width="small"),
                        "涨幅%": st.column_config.NumberColumn("涨幅%", format="%.2f%%", width="small")
                    }
                )

                sector_codes = df_sectors["代码"].tolist()
                default_code = sector_codes[0] if sector_codes else None

                # 优化选择框：显示名称，返回代码
                selected_sector_code = st.selectbox(
                    "选择板块查看详情",
                    options=sector_codes,
                    index=0,
                    format_func=lambda x: f"{code_to_name.get(x, x)} ({x})",  # 下拉框显示：名称 (代码)
                    key=f"select_{zs_type}"
                )

            with col_detail:
                if selected_sector_code:
                    # 获取当前板块名称
                    current_sector_name = code_to_name.get(selected_sector_code, selected_sector_code)

                    # 详情标题：显示 名称
                    st.markdown(f"### 详情: **{current_sector_name}**")
                    st.caption(f"代码: `{selected_sector_code}` | 日期: `{effective_date}`")

                    # --- A. K线图 ---
                    with st.expander("📉 板块K线走势", expanded=False):
                        kline_df = get_sector_kline_data(selected_sector_code)
                        if kline_df is not None and not kline_df.empty:
                            fig = go.Figure()
                            # 红涨绿跌
                            fig.add_trace(go.Candlestick(
                                x=kline_df['date'],
                                open=kline_df['open'],
                                high=kline_df['high'],
                                low=kline_df['low'],
                                close=kline_df['close'],
                                name='K线',
                                increasing_line_color='#ff0000',
                                decreasing_line_color='#00cc00'
                            ))

                            # 成交量颜色与K线对应
                            colors = ['#ff0000' if o <= c else '#00cc00' for o, c in
                                      zip(kline_df['open'], kline_df['close'])]
                            fig.add_trace(go.Bar(
                                x=kline_df['date'],
                                y=kline_df['volume'],
                                name='成交量',
                                marker_color=colors,
                                yaxis='y2',
                                opacity=0.7
                            ))
                            fig.update_layout(
                                title=f"{current_sector_name} 日K",
                                yaxis_domain=[0.3, 1],
                                yaxis2=dict(domain=[0, 0.2], title="成交量"),
                                xaxis_rangeslider_visible=False,
                                height=400,
                                margin=dict(l=0, r=0, t=30, b=0)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("暂无K线数据")

                    # --- B. 子板块 ---
                    # 提前获取子板块信息，用于成分股聚合
                    son_plate = get_son_plate_info(selected_sector_code)

                    if son_plate:
                        with st.expander("📂 子板块详情", expanded=False):
                            df_son = pd.DataFrame(son_plate).sort_values(by="强度", ascending=False)
                            st.dataframe(df_son, use_container_width=True, hide_index=True)

                    # --- C. 成分股 (核心逻辑修改) ---
                    st.divider()
                    st.subheader("📊 板块成分股")

                    stock_data = []
                    is_realtime = (k == 0)

                    if is_realtime:
                        # --- 路径1：当天数据 (CSV + 腾讯 + 子板块聚合) ---
                        sector_map_df = load_sector_map()
                        if sector_map_df is not None:
                            # 1. 收集所有需要查询的板块代码 (主板块 + 子板块)
                            target_plate_codes = [str(selected_sector_code)]

                            # 建立板块代码 -> 名称的映射，方便后续显示来源
                            plate_code_to_name = {str(selected_sector_code): current_sector_name}

                            if son_plate:
                                for sp in son_plate:
                                    sp_code = str(sp['代码'])
                                    target_plate_codes.append(sp_code)
                                    plate_code_to_name[sp_code] = sp['名称']

                            # 2. 在 CSV 中筛选这些板块的股票
                            mask = sector_map_df['板块code'].isin(target_plate_codes)
                            current_sector_stocks = sector_map_df[mask]

                            if not current_sector_stocks.empty:
                                # 建立股票代码 -> 所属板块名称 的映射
                                # 如果一只股票出现在多个子板块，优先显示第一个查到的子板块名称
                                stock_belong_map = {}
                                for _, row in current_sector_stocks.iterrows():
                                    s_code = str(row['股票代码']).zfill(6)
                                    p_code = str(row['板块code'])
                                    if s_code not in stock_belong_map:
                                        stock_belong_map[s_code] = plate_code_to_name.get(p_code, "未知板块")

                                # 去重获取股票代码
                                raw_codes = current_sector_stocks['股票代码'].unique().tolist()
                                tencent_codes = [format_stock_code(c) for c in raw_codes]

                                # 获取实时行情
                                tencent_data = get_stock_data_tencent(tencent_codes)

                                for item in tencent_data:
                                    stock_data.append({
                                        "代码": item['代码'],
                                        "名称": item['名称'],
                                        "涨幅%": item['涨幅%'],
                                        "价格": item['价格'],
                                        "成交额": f"{item['成交额']:.0f}万",
                                        "实际流通值": "-",
                                        # 显示具体的子板块名称
                                        "板块": stock_belong_map.get(item['代码'], current_sector_name),
                                        "连板": "-",
                                        "龙头": "-"
                                    })
                            else:
                                st.warning(f"本地CSV中未找到该板块及其子板块的成分股映射")
                        else:
                            st.error("缺失 stock_sector_data.csv 文件，无法显示当天实时成分股")
                    else:
                        # --- 路径2：历史数据 (长横接口) ---
                        # 历史接口本身包含成分股数据，逻辑不变
                        stock_data = get_stock_data(selected_sector_code, effective_date, k)

                    # --- 数据展示 ---
                    if stock_data:
                        df_stocks = pd.DataFrame(stock_data)

                        # 排序尝试
                        try:
                            df_stocks['涨幅%'] = pd.to_numeric(df_stocks['涨幅%'], errors='coerce')
                            df_stocks.sort_values(by="涨幅%", ascending=False, inplace=True)
                        except Exception:
                            pass

                        # 定义列配置
                        display_cols = [
                            "代码", "名称", "涨幅%", "价格", "成交额",
                            "实际流通值", "板块", "连板", "龙头"
                        ]
                        # 过滤存在的列
                        final_cols = [c for c in display_cols if c in df_stocks.columns]

                        # 配置列样式
                        column_config = {
                            "代码": st.column_config.TextColumn("代码", width="small"),
                            "名称": st.column_config.TextColumn("名称", width="medium"),
                            "涨幅%": st.column_config.NumberColumn("涨幅%", format="%.2f%%", width="small"),
                            "价格": st.column_config.NumberColumn("价格", format="%.2f", width="small"),
                            "成交额": st.column_config.TextColumn("成交额", width="small"),
                            "实际流通值": st.column_config.TextColumn("流通值", width="small"),
                            "板块": st.column_config.TextColumn("所属板块", width="medium"),
                            "连板": st.column_config.TextColumn("连板", width="small"),
                            "龙头": st.column_config.TextColumn("龙头", width="small"),
                        }

                        st.dataframe(
                            df_stocks[final_cols],
                            use_container_width=True,
                            height=500,
                            hide_index=True,
                            column_config=column_config
                        )
                    else:
                        st.info("暂无成分股数据")


if __name__ == "__main__":
    app()