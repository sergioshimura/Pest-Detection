import re
import pandas as pd
from datetime import datetime, timedelta
import argparse

def parse_dji_srt_file(srt_path):
    """
    Lê um arquivo .SRT do DJI Mavic Pro (formato mais novo) e extrai
    o timestamp absoluto e os dados de GPS de cada entrada.
    """
    print(f"Lendo e processando o arquivo SRT: {srt_path}")
    
    # Expressão regular para capturar a data/hora e as coordenadas GPS
    pattern = re.compile(
        r'\d+\n'
        r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n'
        r'HOME\(.*\) (\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\n'
        r'GPS\((.*?),-?(.*?),(\d+)\)',
        re.MULTILINE
    )
    
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo SRT não encontrado em '{srt_path}'")
        return None
    
    matches = pattern.finditer(content)
    telemetry_data = []
    
    for match in matches:
        date_time_str, lon_str, lat_str, alt_str = match.groups()
        
        # Converte a data e hora para um objeto datetime
        absolute_timestamp = datetime.strptime(date_time_str, '%Y.%m.%d %H:%M:%S')
        
        telemetry_data.append({
            'srt_timestamp': absolute_timestamp,
            'latitude': -float(lat_str), # Adiciona o negativo que foi removido pelo regex
            'longitude': float(lon_str),
            'altitude': int(alt_str)
        })
        
    if not telemetry_data:
        print("AVISO: Nenhum dado de telemetria foi extraído. Verifique o formato do arquivo SRT.")
        return None
        
    df = pd.DataFrame(telemetry_data)
    # Define a coluna de timestamp como o índice do DataFrame para buscas rápidas
    df = df.set_index(pd.to_datetime(df['srt_timestamp'])).sort_index()
    
    return df

def main(srt_file):
    """
    Função principal que calcula o offset e inicia o loop de consulta.
    """
    # --- PONTO DE SINCRONIZAÇÃO (fornecido por você) ---
    # Timestamp relativo do vídeo
    srt_relative_time_sync_point = "00:04:40,000"
    # Timestamp absoluto do log de detecção para o ponto acima
    detection_log_sync_point_str = "2025-08-24T17:23:02.670801"
    
    # Carrega todos os dados do SRT
    df_srt = parse_dji_srt_file(srt_file)
    if df_srt is None:
        return

    # Encontra o timestamp absoluto no SRT que corresponde ao tempo relativo
    # O timestamp no SRT é o nome de cada linha (índice)
    try:
        # Extrai a data do primeiro registro para construir o timestamp relativo
        start_date = df_srt.index[0].date()
        h, m, s, ms = map(int, re.split('[:,]', srt_relative_time_sync_point))
        relative_delta = timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)
        
        # Encontra o horário de início no SRT (não é zerado, começa na hora da gravação)
        start_time_of_recording = df_srt.index[0]
        
        srt_absolute_sync_point = start_time_of_recording + relative_delta
        
        # Converte o timestamp da detecção para um objeto datetime
        detection_log_sync_point = datetime.fromisoformat(detection_log_sync_point_str)

        # Calcula o offset (a diferença entre os relógios)
        time_offset = detection_log_sync_point - srt_absolute_sync_point
        
        print("\n--- Sincronização Concluída ---")
        print(f"Timestamp da detecção (referência): {detection_log_sync_point.isoformat()}")
        print(f"Timestamp do SRT (referência):     {srt_absolute_sync_point.isoformat()}")
        print(f"Offset calculado (Computador - Drone): {time_offset}")
        print("---------------------------------\n")

    except Exception as e:
        print(f"ERRO ao calcular o offset: {e}. Verifique os pontos de sincronização.")
        return

    print("Agora você pode digitar os timestamps de detecção.")
    print("Para sair, digite 'sair' ou 'exit'.")

    while True:
        timestamp_str = input("\nDigite o timestamp da detecção (ex: 2025-08-24T17:23:02.670801): ")
        
        if timestamp_str.lower() in ['sair', 'exit', 'q']:
            print("Encerrando o programa.")
            break
        
        try:
            # Converte o timestamp inserido pelo usuário
            target_dt = datetime.fromisoformat(timestamp_str)
            
            # Aplica o offset para "traduzir" o tempo para o referencial do drone
            corrected_dt = target_dt - time_offset
            
            print(f"Buscando pelo tempo corrigido (referencial do drone): {corrected_dt.isoformat()}")

            # Encontra o índice do timestamp mais próximo no DataFrame do SRT
            closest_index = df_srt.index.get_indexer([corrected_dt], method='nearest')[0]
            closest_data = df_srt.iloc[closest_index]
            time_difference = closest_data.name - corrected_dt

            print("-" * 40)
            print("Coordenadas encontradas para o momento mais próximo:")
            print(f"  - Latitude:  {closest_data['latitude']}")
            print(f"  - Longitude: {closest_data['longitude']}")
            print(f"  - Altitude:  {closest_data['altitude']} metros")
            print(f"\nTimestamp do GPS: {closest_data.name.isoformat()}")
            print(f"Diferença de tempo (precisão): {time_difference.total_seconds() * 1000:.2f} milissegundos")
            print("-" * 40)

        except ValueError:
            print("ERRO: Formato de timestamp inválido. Use o formato AAAA-MM-DDTHH:MM:SS.ffffff")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Busca coordenadas em um arquivo .SRT a partir de um timestamp de detecção, corrigindo o offset.")
    parser.add_argument("srt_file", help="Caminho para o arquivo .SRT de telemetria do drone.")
    
    args = parser.parse_args()
    
    main(args.srt_file)
