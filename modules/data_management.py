import glob
import json
import os
import time
import urllib
import zipfile

import ipykernel
import pandas as pd
import requests
import selenium
from google_drive_downloader import GoogleDriveDownloader as gdd
from notebook import notebookapp
from selenium.webdriver.common.keys import Keys

#################################
# OBTAIN PATHS AND MAKE FOLDERS #
#################################


def notebook_path():
    """Returns the absolute path of the Notebook or None if it cannot be determined
    NOTE: works only when the security is token-based or there is also no password
    """
    connection_file = os.path.basename(ipykernel.get_connection_file())
    kernel_id = connection_file.split("-", 1)[1].split(".")[0]

    for srv in notebookapp.list_running_servers():
        try:
            if (
                srv["token"] == "" and not srv["password"]
            ):  # No token and no password, ahem...
                req = urllib.request.urlopen(srv["url"] + "api/sessions")
            else:
                req = urllib.request.urlopen(
                    srv["url"] + "api/sessions?token=" + srv["token"]
                )
            sessions = json.load(req)
            for sess in sessions:
                if sess["kernel"]["id"] == kernel_id:
                    return os.path.join(srv["notebook_dir"], sess["notebook"]["path"])
        except Exception:
            pass  # There may be stale entries in the runtime directory
    return None


def make_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


#########################
# DOWNLOAD SOURCE FILES #
#########################


def download_file_maps(route="./local/data/src_general/", filename="colombia.geo.json"):

    gdd.download_file_from_google_drive(
        file_id="1wEiDe2B_ojoaLUnV3Ik67t_YpAC2nbPA",
        dest_path=route + filename,
        unzip=False,
        showsize=True,
        overwrite=True,
    )
    return


def download_files_processed_dengue(route="./local/data/prepared_dengue/"):
    gdd.download_file_from_google_drive(
        file_id="1GAteakYZ8LlNFsQG1B8B3-E_1mlKy7qj",
        dest_path=route + "dengue_weekly_2007_2020.csv",
        unzip=False,
        showsize=True,
        overwrite=True,
    )
    return


def download_file_population(
    route="./local/data/src_general/", filename="population.csv"
):

    gdd.download_file_from_google_drive(
        file_id="1RU2C4DoAubhXEhfVYLOtL4Yjg1LPERIc",
        dest_path=route + filename,
        unzip=False,
        showsize=True,
        overwrite=True,
    )
    return


def download_file_year(route="./local/data/src_general/", filename="data_per_year.csv"):

    gdd.download_file_from_google_drive(
        file_id="1Bgya5O3FtPo6zasYaKRc3J-U_l2ZcYHw",
        dest_path=route + filename,
        unzip=False,
        showsize=True,
        overwrite=True,
    )
    return


def download_file_departments(
    route="./local/data/src_general/", filename="departments.csv"
):

    gdd.download_file_from_google_drive(
        file_id="1ImNzdFwQF91aA4qE_7XKpOU7AFK1f7WS",
        dest_path=route + filename,
        unzip=False,
        showsize=True,
        overwrite=True,
    )
    return


def download_rutinarias(route="./local/data/src_general/rutinarias_dengue/"):
    # Alternate path:
    rutinarias = [str(i) for i in range(2007, 2020)] + ["2020p", "2021p"]
    for rutinaria in rutinarias:
        filename = "rutinaria_" + rutinaria + ".xlsx"
        url = f"http://portalsivigila.ins.gov.co/VigilanciaRutinaria/rutinaria_{rutinaria}.xlsx"
        r = requests.get(url, allow_redirects=True)
        open(route + filename, "wb").write(r.content)


def download_file_sstoi(route="./local/data/src_general/", filename="sstoi.txt"):
    url = "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
    r = requests.get(url, allow_redirects=True)
    open(route + filename, "wb").write(r.content)


def download_file_oni(route="./local/data/src_general/", filename="oni.txt"):
    url = "https://psl.noaa.gov/data/correlation/oni.data"
    r = requests.get(url, allow_redirects=True)
    open(route + filename, "wb").write(r.content)


def download_file_tni(route="./local/data/src_general/", filename="tni.txt"):
    url = "https://psl.noaa.gov/data/correlation/tni.data"
    r = requests.get(url, allow_redirects=True)
    open(route + filename, "wb").write(r.content)


def download_file_meiv2(route="./local/data/src_general/", filename="meiv2.txt"):
    url = "https://psl.noaa.gov/enso/mei/data/meiv2.data"
    r = requests.get(url, allow_redirects=True)
    open(route + filename, "wb").write(r.content)


def download_file_car(route="./local/data/src_general/", filename="car.txt"):
    url = "https://psl.noaa.gov/data/correlation/CAR_ersst.data"
    r = requests.get(url, allow_redirects=True)
    open(route + filename, "wb").write(r.content)


def download_file_nta(route="./local/data/src_general/", filename="nta.txt"):
    url = "https://psl.noaa.gov/data/correlation/NTA_ersst.data"
    r = requests.get(url, allow_redirects=True)
    open(route + filename, "wb").write(r.content)


def download_data_with_selenium(
    department, municipality, variable, interval, dl_folder
):
    variable_codes = {
        "TEMPERATURA": "TA2_AUT_60",
        "HUM RELATIVA": "HRA2_AUT_60",
        "PRECIPITACION": "PTPM_CON",
        "VEL VIENTO": "VV_AUT_10",
        "RAD SOLAR": "RSGVAL_AUT_60",
    }
    options = selenium.webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"download.default_directory": dl_folder})
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = selenium.webdriver.Chrome(chrome_options=options)
    driver.get("http://dhime.ideam.gov.co/atencionciudadano/")
    got_modal = False
    # Find the modal and click it out
    while not got_modal:
        try:
            elem = driver.find_element_by_xpath(
                '//*[@id="jimu_dijit_CheckBox_0"]/div[1]'
            )
            elem.click()
            time.sleep(1)
            elem = driver.find_element_by_xpath(
                '//*[@id="widgets_Splash_Widget_32"]/div[2]/div[2]/div[2]/div[3]'
            )
            elem.click()
            time.sleep(0.25)
            got_modal = True
        except Exception:
            time.sleep(1)
            print("Retrying get modal")

    got_datepickers = False

    while not got_datepickers:
        try:
            elem = driver.find_element_by_xpath('//*[@id="datepicker"]')
            elem.clear()
            time.sleep(0.25)
            elem.send_keys(interval[0])
            time.sleep(0.25)
            elem = driver.find_element_by_xpath('//*[@id="datepicker1"]')
            elem.clear()
            time.sleep(0.25)
            elem.send_keys(interval[1])
            time.sleep(1)
            got_datepickers = True
        except Exception:
            time.sleep(5)
            print("Retrying get datepickers")
    got_vars = False
    while not got_vars:
        try:
            elem = driver.find_element_by_xpath(
                '//*[@id="pnlEstandar"]/table/tbody/tr[1]/td[2]/span'
            )
            elem.click()
            elem.send_keys(variable)
            elem.send_keys(Keys.ENTER)
            time.sleep(1)
            input_element = driver.find_element_by_xpath(
                '//*[@id="DatosBuscar"]/tbody/tr[1]/td[1]/input'
            )
            onclick_value = "cargarEtiquetaEst('{}','')".format(
                variable_codes[variable]
            )
            driver.execute_script(
                'arguments[0].setAttribute("onclick","{}")'.format(onclick_value),
                input_element,
            )
            input_element.click()
            time.sleep(3)
            got_vars = True
        except Exception:
            time.sleep(5)
            print("Retrying variables")

    elem = driver.find_element_by_xpath('//*[@id="first"]/table/tbody/tr[1]/td[2]/span')
    elem.click()
    elem.send_keys(department)
    elem.send_keys(Keys.ENTER)
    time.sleep(2)
    elem = driver.find_element_by_xpath('//*[@id="first"]/table/tbody/tr[2]/td[2]/span')
    elem.click()
    elem.send_keys(municipality)
    elem.send_keys(Keys.ENTER)
    time.sleep(2)
    trs_stations = driver.find_elements_by_xpath(
        '//*[@id="contenidoCantidadMetadata"]/table/tbody/tr'
    )
    count = 0
    for tr_station in trs_stations:
        probable_values = int(tr_station.find_elements_by_tag_name("td")[-1].text)
        if probable_values > 0 and count <= 7:
            select_box = tr_station.find_elements_by_tag_name("input")[0]
            select_box.click()
            count += 1
    if len(trs_stations) > 0:
        for tr_station in reversed(trs_stations):
            probable_values = int(tr_station.find_elements_by_tag_name("td")[-1].text)
            if probable_values > 0 and count <= 9:
                select_box = tr_station.find_elements_by_tag_name("input")[0]
                if select_box.is_selected() == False:
                    select_box.click()
                    count += 1
    if count == 0:
        driver.close()
        return False
    else:
        elem = driver.find_element_by_xpath('//*[@id="first"]/div[5]/div')
        elem.click()
        time.sleep(1)
        elem = driver.find_element_by_xpath('//*[@id="second"]/div/div[3]/div[1]')
        elem.click()
        time.sleep(1)
        elem = driver.find_element_by_xpath(
            '//*[@id="dijit_ConfirmDialog_1"]/div[3]/span[1]'
        )
        elem.click()
        time.sleep(25)
        driver.close()
    return True


############################
# DOWNLOAD FROM SOCRATA API#
############################

# Downloads from API
def get_stations_from_municipality(client, dataset, municipio):
    done = False
    results_df = None
    while not done:
        try:
            results = client.get(
                dataset,
                limit=1000,
                select="distinct CodigoEstacion, CodigoSensor, NombreEstacion, Latitud, Longitud, DescripcionSensor, UnidadMedida",
                municipio=municipio,
            )
            results_df = pd.DataFrame.from_records(results)
            done = True
        except Exception as E:
            print(E, "retrying")
    return results_df


def get_time_series_from_station(
    client, dataset, municipio, codigoestacion, limit=1000000
):
    results_df = None
    done = False
    while not done:
        try:
            results = client.get(
                dataset,
                limit=limit,
                select="*",
                municipio=municipio,
                codigoestacion=codigoestacion,
                order="fechaobservacion DESC",
            )
            results_df = pd.DataFrame.from_records(results)
            done = True
        except Exception as E:
            print(E, "retrying")
    return results_df


def group_variable(df, freq="hourly"):
    df["fechaobservacion"] = pd.to_datetime(df["fechaobservacion"])
    df["fecha"] = df["fechaobservacion"].dt.date
    df["valorobservado"] = df["valorobservado"].apply(float)
    if freq == "hourly":
        df["hora"] = df["fechaobservacion"].dt.hour
        df = (
            df.groupby(
                [
                    "codigoestacion",
                    "codigosensor",
                    "nombreestacion",
                    "departamento",
                    "municipio",
                    "zonahidrografica",
                    "latitud",
                    "longitud",
                    "descripcionsensor",
                    "unidadmedida",
                    "fecha",
                    "hora",
                ]
            )
            .mean()
            .reset_index()
        )
        df["fechaobservacion"] = (
            df["fecha"].apply(str) + "T" + df["hora"].apply(str) + ":00:00.000"
        )
    elif freq == "daily":
        df = (
            df.groupby(
                [
                    "codigoestacion",
                    "codigosensor",
                    "nombreestacion",
                    "departamento",
                    "municipio",
                    "zonahidrografica",
                    "latitud",
                    "longitud",
                    "descripcionsensor",
                    "unidadmedida",
                    "fecha",
                ]
            )
            .sum()
            .reset_index()
        )
        df["fechaobservacion"] = df["fecha"].apply(str) + "T00:00:00.000"
    df = df[
        [
            "codigoestacion",
            "codigosensor",
            "fechaobservacion",
            "valorobservado",
            "nombreestacion",
            "departamento",
            "municipio",
            "zonahidrografica",
            "latitud",
            "longitud",
            "descripcionsensor",
            "unidadmedida",
        ]
    ]
    return df


def API_to_IDEAM_series(df):
    df.columns = [
        "CodigoEstacion",
        "CodigoSensor",
        "Fecha",
        "Valor",
        "NombreEstacion",
        "Departamento",
        "Municipio",
        "AreaOperativa",
        "Latitud",
        "Longitud",
        "Etiqueta",
        "Categoria",
    ]
    df["Altitud"] = ""
    df["FechaInstalacion"] = ""
    df["FechaSuspension"] = ""
    df["Frecuencia"] = ""
    df["Grado"] = ""
    df["NivelAprobacion"] = ""
    df["DescripcionSerie"] = ""
    df["Entidad"] = ""
    df["IdParametro"] = ""
    df["Calificador"] = ""
    df["CodigoEstacion"] = df["CodigoEstacion"].apply(int)
    df = df[
        [
            "CodigoEstacion",
            "NombreEstacion",
            "Latitud",
            "Longitud",
            "Altitud",
            "Categoria",
            "Entidad",
            "AreaOperativa",
            "Departamento",
            "Municipio",
            "FechaInstalacion",
            "FechaSuspension",
            "IdParametro",
            "Etiqueta",
            "DescripcionSerie",
            "Frecuencia",
            "Fecha",
            "Valor",
            "Grado",
            "Calificador",
            "NivelAprobacion",
        ]
    ]
    return df


##########################
# MANAGE PARAMETERS FILE #
##########################


def read_cities_file(
    path="./params.csv",
    rows_to_eval=[
        "stations_temp",
        "stations_hum",
        "stations_prec",
        "stations_rad",
        "range_temp",
        "range_hum",
    ],
):
    df = pd.read_csv(
        path, sep=",", index_col=None, dtype={"code": str, "starting_date": str}
    )
    for row in rows_to_eval:
        df.loc[:, row] = df.loc[:, row].apply(lambda x: eval(x))
    return df
