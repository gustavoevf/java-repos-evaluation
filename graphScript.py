import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def is_file_empty(file_path):
    return os.stat(file_path).st_size == 0  # Verifica se o tamanho do arquivo é 0

def load_csv_with_columns(file_path, required_columns):
    # Carregar as colunas disponíveis do arquivo
    df = pd.read_csv(file_path, encoding='latin1', nrows=0)  # Carregar apenas os nomes das colunas
    available_columns = df.columns.tolist()
    
    # Filtrar apenas as colunas disponíveis
    cols_to_load = [col for col in required_columns if col in available_columns]
    
    # Carregar o arquivo com as colunas disponíveis
    df = pd.read_csv(file_path, encoding='latin1', usecols=cols_to_load)
    
    return df

def calculate_age(created_at):
    """Calcula a idade do repositório em anos a partir da data de criação"""
    created_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.utcnow()
    age_in_years = (current_date - created_date).days / 365
    return age_in_years

def load_csv_files(root_dir):
    """Carrega todos os arquivos CSV da pasta analysis_results e subpastas."""
    data = []
    selected_columns = ['loc', 'cbo', 'wmc', 'rfc']  # Ajuste conforme necessário
    selected_columnsclass = ['loc', 'cbo', 'wmc', 'rfc', 'dit', 'lcom']  # Ajuste conforme necessário

    for subdir, _, files in os.walk(root_dir):
        method_files = [os.path.join(subdir, f) for f in files if 'method' in f and f.endswith('.csv')]
        class_files = [os.path.join(subdir, f) for f in files if 'class' in f and f.endswith('.csv')]
        
        for method_path in method_files:
            for class_path in class_files:
                if is_file_empty(method_path):
                    print(f"Aviso: O arquivo {method_path} está vazio e será ignorado.")
                    continue  # Pule esse arquivo
                if is_file_empty(class_path):
                    print(f"Aviso: O arquivo {method_path} está vazio e será ignorado.")
                    continue  # Pule esse arquivo
                methods_df = load_csv_with_columns(method_path, selected_columns)
                class_df = load_csv_with_columns(class_path, selected_columnsclass)
                data.append((methods_df, class_df))
    return data

def analyze_and_plot(df_method_or_class, df_infos, title, x_col, y_col):
    """
    Função para analisar e gerar gráficos de dispersão (scatter plot) com as métricas fornecidas.
    
    Parâmetros:
    - df_method_or_class: DataFrame contendo os dados de métodos ou classes.
    - df_infos: DataFrame contendo informações adicionais (como 'stars', 'loc', etc.).
    - title: Título do gráfico.
    - x_col: Nome da coluna para o eixo X.
    - y_col: Nome da coluna para o eixo Y.
    """
    # Checando se as colunas existem nos DataFrames
    if y_col not in df_method_or_class.columns:
        print(f"Colunas{y_col} não encontradas no DataFrame de métodos ou classes!")
        return
    
    if x_col != "loc":
        if x_col not in df_infos.columns:
            print(f"Colunas {x_col} não encontradas no DataFrame de informações!")
            return
    
    # Combinando os DataFrames de métodos/classes com as informações adicionais
    combined_df = pd.merge(df_method_or_class, df_infos, left_index=True, right_index=True)
    if x_col == "created_at":
        combined_df['created_at'] = pd.to_datetime(combined_df['created_at'])
    
    # Analisando a correlação entre as duas variáveis
    correlation = combined_df[x_col].corr(combined_df[y_col])
    
    # Configuração do gráfico
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=combined_df[x_col], y=combined_df[y_col], color='b', alpha=0.6)
    
    # Título e labels
    plt.title(f'{title}\nCorrelação: {correlation:.2f}', fontsize=16)
    plt.xlabel(x_col, fontsize=14)
    plt.ylabel(y_col, fontsize=14)
    
    # Exibindo o gráfico
    plt.show()

def main():
    root_dir = 'analysis_results'
    datasets = load_csv_files(root_dir)
    
    # Mesclar todos os datasets em um único dataframe
    combined_methods = pd.concat([df[0] for df in datasets], ignore_index=True)
    combined_classes = pd.concat([df[1] for df in datasets], ignore_index=True)
    file_path = './github_top_1000.csv'
    selected_columnsInfos = ['stargazers_count', 'releases', 'created_at']  # Ajuste conforme necessário
    combined_infos = pd.read_csv(file_path, usecols=selected_columnsInfos)
    
    # Métricas de processo
    pop_col = 'stargazers_count'  # Popularidade (número de estrelas) - NÃO ENCONTRADO, PRECISA SER ADICIONADO
    size_col = 'loc'  # Tamanho (Linhas de Código)
    activity_col = 'releases'  # Atividade (número de releases) - NÃO ENCONTRADO, PRECISA SER ADICIONADO
    mature_col = 'created_at'  # Maturidade (idade em anos) - NÃO ENCONTRADO, PRECISA SER ADICIONADO
    
    # Métricas de qualidade
    quality_metrics = ['cbo', 'wmc', 'rfc', 'dit', 'lcom']
    
    # Gerar gráficos para cada RQ
    for quality_col in quality_metrics:
        analyze_and_plot(combined_methods, combined_infos, "RQ 01: Popularidade vs " + quality_col, pop_col, quality_col)
        analyze_and_plot(combined_methods, combined_infos, "RQ 02: Maturidade vs " + quality_col, mature_col, quality_col)
        analyze_and_plot(combined_methods, combined_infos, "RQ 03: Atividade vs " + quality_col, activity_col, quality_col)
        analyze_and_plot(combined_classes, combined_infos, "RQ 04: Tamanho vs " + quality_col, size_col, quality_col)
    
if __name__ == "__main__":
    main()
