from selenium import webdriver # usei a versão pip install selenium==4.2.0
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

url_code = 'https://www.skoob.com.br/login/'

PATH = 'C:/GIT/Skoob_Leituras/Driver/chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(chrome_options=options,service=Service(ChromeDriverManager().install()))

#driver = webdriver.Chrome(executable_path = PATH, chrome_options=options)
sleep(3)

usuario = os.getenv("usuario")
senha = os.getenv("senha")

# botão logar com facebook

driver.get(url_code)
sleep(2)

#ok na ferramenta de cookie
driver.find_element_by_xpath("//*[@id='ng-app']/div/div[3]/a").click()

# mandar usuario
driver.find_element_by_id("UsuarioEmail").send_keys(usuario)
sleep(1)

# mandar senha
driver.find_element_by_id("UsuarioSenha").send_keys(senha)
sleep(1)

# clicar em entrar
driver.find_element_by_xpath("//*[@id='login-box-col02']/form/div/div/input").click()
sleep(1)

# clicar em opções
driver.find_element_by_xpath("//*[@id='topo-menu-conta']").click()
sleep(1)

# clicar em minha estante
driver.find_element_by_xpath("//*[@id='topo-menu-conta-hover']/li[2]/a").click()
sleep(1)

texto = driver.find_element_by_xpath("//*[@id='corpo']/div/div[4]/div[1]/div[1]/ul/li[1]/div[2]/span").text
print(texto)

#lista_ultimo = int(texto) % 36

next_pages = int(int(texto)/36)

rating = []
num_aval = []
nome = []
leram = []
querem_ler = []
relendo = []
abandonos = []
resenhas = []
autor = []
editora = []
ano = []
paginas = []

#entrar em cada livro de cada pagina e guardar estatisticas
try:
    #Passando por cada página, cada uma delas contém 36 registros   
    for j in range(0,next_pages+36,1):
        print("Página:",j+1)
        #Passando por cada livro
        for i in range(1,1+1,1):
            print("Livro:",i)

            if j>0:
                # Botão de cada virada de página
                driver.find_element_by_xpath("//*[@id='corpo']/div/div[4]/div[2]/div[3]/div[2]/ul/li["+str(3+j)+"]/a").click()
                sleep(2)
            # Clicando em cada livro
            driver.find_element_by_xpath("//*[@id='corpo']/div/div[4]/div[2]/div[2]/ul/li["+str(i)+"]/div/div[3]/a/div[2]/img").click()

            sleep(1)
            #Coletando estatisticas de cada livro para o nome
            rating.append(driver.find_element_by_xpath("//*[@id='pg-livro-box-rating']/span").text)
            num_aval.append( (driver.find_element_by_xpath("//*[@id='pg-livro-box-rating-avaliadores-numero']").text.replace(' avaliações', '').replace('.','') ) )
            
            # O 4 volumes de Sherlock tem o mesmo nome, logo peguei outra informação
            if driver.find_element_by_xpath("//*[@id='pg-livro-menu-principal-container']/strong").text == 'Sherlock Holmes':
                nome.append(driver.find_element_by_xpath("//*[@id='pg-livro-menu-principal-container']/h3").text)
            else:
                nome.append(driver.find_element_by_xpath("//*[@id='pg-livro-menu-principal-container']/strong").text)

            leram.append( (driver.find_element_by_xpath("//*[@id='livro-perfil-status']/div[7]/b/a").text).replace('.','') )
            querem_ler.append( (driver.find_element_by_xpath("//*[@id='livro-perfil-status']/div[6]/b/a").text).replace('.','') )
            relendo.append( (driver.find_element_by_xpath("//*[@id='livro-perfil-status']/div[5]/b/a").text).replace('.','') )
            abandonos.append( (driver.find_element_by_xpath("//*[@id='livro-perfil-status']/div[3]/b/a").text).replace('.','') )
            resenhas.append( (driver.find_element_by_xpath("//*[@id='livro-perfil-status']/div[2]/b/a").text).replace('.','') )

            if driver.find_element_by_xpath("//*[@id='pg-livro-menu-principal-container']/a[1]").text == 'Editar':
                autor.append(driver.find_element_by_xpath("//*[@id='pg-livro-menu-principal-container']/i").text)
            else:
                autor.append(driver.find_element_by_xpath("//*[@id='pg-livro-menu-principal-container']/a[1]").text)

            geral = driver.find_element_by_class_name("sidebar-desc").text
            editora.append(geral[(geral.find('Editora')):].replace('Editora: ', ''))

            year = geral[(geral.find('Ano')): (geral.find('Ano'))+11 ]
            ano.append(re.findall("\d+", year)[0]) #extraindo apenas o numero

            page = geral[(geral.find('Páginas')): (geral.find('Páginas'))+19 ]
            paginas.append(re.findall("\d+", page)[0]) #extraindo apenas o numero

            sleep(2) 
            #Volta para a página anterior depois de coletar as estatísticas
            driver.back()
            sleep(1)

except NoSuchElementException:
    print("Terminado Livros")

rating = list(map(float, rating))
num_aval = list(map(int, num_aval))
leram = list(map(int, leram))
querem_ler = list(map(int, querem_ler))
relendo = list(map(int, relendo))
abandonos = list(map(int, abandonos))
resenhas = list(map(int, resenhas))
ano = list(map(int, ano))
paginas = list(map(int, paginas))


tabela_consolidada = pd.DataFrame(
    {'nota': rating,
     'avaliacoes': num_aval,
     'nome': nome,
     'leram': leram,
     'querem_ler': querem_ler,
     'relendo': relendo,
     'abandonos': abandonos,
     'resenhas': resenhas,
     'autor': autor,
     'editora': editora,
     'ano': ano,
     'paginas': paginas,
    })
    
tabela_consolidada.to_csv('C:\GIT\Skoob_Leituras\Bases\livros_'+ str(datetime.now().strftime('%d_%m_%Y')) +'.csv', index=False)

# Coletar informações do autor

# url_code1 = 'https://www.skoob.com.br/autor/lista/'

# autor_genero = []
# nascimento = []
# local = []

# try:
#     for i in autor:
#         # Página Escritóres
#         print(i)
#         driver.get(url_code1)
#         sleep(1)
#         driver.find_element_by_id("BuscaTag").send_keys(i)
#         sleep(1)
#         driver.find_element_by_xpath("//*[@id='corpo']/div[1]/form/input[2]").click()
#         sleep(1)
#         driver.find_element_by_xpath("//*[@id='corpo']/div[2]/div/div[2]/div[3]/div[1]/strong/a").click()
#         sleep(2)
#         driver.refresh()
#         autor_genero.append(driver.find_element_by_xpath("//*[@id='box-generos']/text()[1]").text)
#         nascimento.append(driver.find_element_by_xpath("//*[@id='box-generos']/text()[2]").text)
#         local.append(driver.find_element_by_xpath("//*[@id='box-generos']/span/text()").text)
#         sleep(2)
#         driver.get(url_code1)
        

# except NoSuchElementException:
#     print("Terminado Autor")

# print(autor_genero)