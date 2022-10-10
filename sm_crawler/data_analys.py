import os, json
import pandas as pd
import matplotlib.pyplot as plt
JSON_PATH = os.getcwd() + os.sep + 'data/json'

def convert_str_json_to_df(str_json_file):
    json_list = []
    with open(str_json_file, 'r', encoding='utf-8') as f:
        data_list = f.readlines()
        for data in data_list:
            json_list.append(json.loads(data))
    # print(json_list)
    return pd.json_normalize(json_list)

def  plt_draw_line(tag_df, key): 
    df = tag_df
    df['publish_time'] = pd.to_datetime(df['publish_time'], errors = 'coerce')
    df = df.set_index(df['publish_time'] )
    plt.figure(figsize=(20,10))
    df[key].plot(title='Raw Data')
    plt.tick_params(labelsize=20)
    plt.title = 'raw data' + key
    plt.grid()
    
def df_date_cut_sum(df, sum_flag, threshold, date_start, date_end=None):
    df['publish_time'] = pd.to_datetime(df['publish_time'], errors = 'coerce')
    df = df.set_index(df['publish_time'] )
    df_cut = df[df['publish_time']>=date_start]
    if date_end:
        df_cut = df_cut[df_cut['publish_time']<=date_end]
    comment_max = df_cut['comment_num'].max()
    print("Post comment mean: %d" % df_cut['comment_num'].mean())
    print("Post comment max: %d" % comment_max)
    print("Post comment max content: %s" % df_cut[df_cut['comment_num']==comment_max]['content'])
    print("Post comment larger than %d: %d" % (threshold, df_cut[df_cut['comment_num']>=threshold]['comment_num'].count()))
    return df_cut.resample(sum_flag).sum()    
    
def df_date_cut_date(df, date_start=None, date_end=None):
    df['date'] = pd.to_datetime(df['date'], errors = 'coerce')
    df = df.set_index(df['date']).sort_index(ascending=False)
    if date_start:
        df = df[df['date']>=date_start]
    if date_end:
        df = df[df['date']<=date_end]    
    return df    

def df_plt_line(df, key):    
    # font = FontProperties(fname="SimHei.ttf", size=14) 
    plt.rcParams['font.sans-serif'] = ['SimHei']         
    plt.figure(figsize=(20,10))
    plt.title = key
    df[key].plot(title=key)
    plt.tick_params(labelsize=20)
    plt.grid() 

def save_df_sum2csv(df_sum, csv_tag, cut_flag, topic_path=None):
    csv_root = './data' + '/csv/'
    csv_path = csv_root + csv_tag + '_' + cut_flag + '.csv'
    df_sum.to_csv(csv_path)


if __name__ == '__main__':
    # account_name = 'Lula0925-30'
    account_name = 'jairmessias.bolsonaro0925-30'
    json_file = JSON_PATH + os.sep + account_name + '.json'
    df = convert_str_json_to_df(json_file)
    cut_flag = 'W'
    d_df = df_date_cut_sum(df, cut_flag, 0, '2022-08-25')
    df_plt_line(d_df, 'comment_num')
    save_df_sum2csv(d_df, account_name, cut_flag)