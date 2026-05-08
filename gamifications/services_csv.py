import csv
import os
from django.contrib.auth import get_user_model
from django.core.files.base import File
from gamifications.models import UserPointsHistory

UsuarioModel = get_user_model()


class ExportHistoricalPointsCSVService():
    """ Class Seleciona os dados da Base e cria o CSV """

    def __init__(self, instance):
        self.instance = instance

    def convert_to_csv_history(self, results):
        """ Recebe os dados que retornaram do select, cria o arquivo CSV e escreve os dados da consulta """

        # --------
        #   Arquivo que sera criado
        csv_file_name = 'media/gamifications/relatorios/relatorio_de_pontos.csv'

        # --------
        #   Abre o arquivo e escreve o cabeçalho
        with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:

            fieldnames = [
                "full_name",
                "email",
                "cpf",
                "type_points",
                "points",
                "award",
                "gain",
                "created_at"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # --------
            #   Para cada um dos dados recebidos
            row_register = {}
            for obj in results:
                
                created_at = obj.created_at
                type_points = obj.type_points
                points = obj.points
                gain = obj.gain

                full_name = obj.user.full_name
                email = obj.user.email
                cpf = obj.user.cpf

                try:
                    award_name = obj.award.name
                except:
                    award_name = ""

                # --------
                #   cria o dicionario da linha com o objeto e o valor
                row_register["full_name"] = full_name
                row_register["email"] = email
                row_register["cpf"] = cpf
                row_register["type_points"] = type_points
                row_register["points"] = points
                row_register["award"] = award_name
                row_register["gain"] = gain
                row_register["created_at"] = created_at

                # --------
                #   Registra os dados no arquivo
                writer.writerow(row_register)

        csvfile.close()
        with open(csv_file_name, 'r', encoding='utf-8') as csvfile:
            self.instance.file = File(csvfile, name=os.path.basename(csvfile.name))
            self.instance.generated_successfully = True
            self.instance.save()

    def handle(self):
        """ seleciona um conjunto de dados na base, chama uma função passando o solicidado e retorna se foi bem sucedido ou não. """
        start_date = self.instance.start_date
        end_date = self.instance.end_date

        queryset = UserPointsHistory.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            deleted=False,
            ).select_related("user", "award")

        try:
            #print('convertendo')
            #print(queryset.query)
            self.convert_to_csv_history(queryset)

            # from django.db import connection
            #print('Quantidade de querys finais: ', len(connection.queries))
            #print(connection.queries)
            return True
        except Exception as err:
            print('ERRO: ' + str(err))
            return False
