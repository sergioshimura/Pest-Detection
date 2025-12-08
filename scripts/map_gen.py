import folium
import pandas as pd
import io
from folium.features import DivIcon

# --- Seus Dados ---
dados_str = """timestamp,latitude,longitude,label
04:40,-23.057500,-46.943806,4
05:06,-23.057500,-46.944300,9
05:14,-23.057500,-46.944500,1
05:31,-23.057500,-46.944400,3
06:01,-23.057400,-46.944000,8
06:17,-23.057400,-46.943900,10
06:48,-23.057400,-46.943900,6
"""
df = pd.read_csv(io.StringIO(dados_str))

# --- Criação do Mapa ---
ponto_central = [df['latitude'].mean(), df['longitude'].mean()]
mapa = folium.Map(location=ponto_central, zoom_start=19, max_zoom=20)

folium.TileLayer(
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attr='Google',
    name='Google Satellite',
    overlay=False,
    control=True
).add_to(mapa)

print("Adicionando balões de anotação...")

# Dicionário para contar e deslocar pontos sobrepostos
coord_counts = {}
# Deslocamentos horizontais em pixels para o 1º, 2º, 3º ponto no mesmo local
offsets_x = [0, 35, -35, 70, -70] 


# Itera sobre cada ponto para criar o balão
for indice, linha in df.iterrows():
    label_personalizado = linha['label']
    coord = (linha['latitude'], linha['longitude'])

    # Conta a ocorrência desta coordenada
    coord_counts[coord] = coord_counts.get(coord, 0) + 1
    count = coord_counts[coord]
    
    # Seleciona o deslocamento horizontal
    offset_x = offsets_x[(count - 1) % len(offsets_x)]

    # --- NOVO HTML PARA O BALÃO COM SETA ---
    html_balao = f'''
    <div style="
        position: absolute;
        transform: translate(-50%, -100%); /* Posiciona o balão acima do ponto */
        background-color: white; 
        border: 1.5px solid black; 
        border-radius: 5px; 
        padding: 3px 6px; 
        font-size: 10pt; 
        font-weight: bold;
        white-space: nowrap; /* Impede que o texto quebre a linha */
    ">
        {label_personalizado}
        <div style="
            position: absolute;
            bottom: -8px; /* Posiciona a seta abaixo da caixa */
            left: 50%;
            transform: translateX(-50%);
            width: 0; 
            height: 0; 
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 8px solid black; /* Cor da borda da seta */
        "></div>
        <div style="
            position: absolute;
            bottom: -7px; /* Seta interna para dar a cor de fundo */
            left: 50%;
            transform: translateX(-50%);
            width: 0; 
            height: 0; 
            border-left: 7px solid transparent;
            border-right: 7px solid transparent;
            border-top: 7px solid white;
        "></div>
    </div>
    '''
    
    folium.map.Marker(
        [linha['latitude'], linha['longitude']],
        icon=DivIcon(
            icon_size=(0,0), # O tamanho é definido pelo próprio HTML
            icon_anchor=(offset_x, 15), # Aplica o deslocamento horizontal e um pequeno ajuste vertical
            html=html_balao,
        )
    ).add_to(mapa)

coordenadas_da_trajetoria = df[['latitude', 'longitude']].values.tolist()
folium.PolyLine(coordenadas_da_trajetoria, color='cyan', weight=2.5, opacity=0.8).add_to(mapa)

folium.LayerControl().add_to(mapa)

nome_do_arquivo = 'mapa_baloes_final.html'
mapa.save(nome_do_arquivo)
print(f"\nMapa final com balões gerado com sucesso! Abra o arquivo '{nome_do_arquivo}'.")