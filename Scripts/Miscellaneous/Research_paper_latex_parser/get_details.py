from os.path import isfile, join
import re
import json
from os import listdir
import argparse
import os
from tqdm import tqdm


class essential_data:
    """
    Extract essential data from the tex document.
    Essential data includes - title, author, abstract, introduction, conclusions, results, acknowledgments.
    """

    def __init__(self, tex_data):
        self.tex_data = tex_data

    def get_elements(self):
        data = self.tex_data
        data_dict = {}

        sections = re.findall(r'section{(.*?)\\', data, re.S)
        for obj in sections:
            h = re.findall(r'(.*?)}', obj, re.S)
            c = obj.replace(h[0]+"}", ' ')
            data_dict['%s' % (h[0])] = '%s' % (c)
            data = data.replace("section{" + obj, " ")

        begins = re.findall(r'\\begin{(.*?)\\end', data, re.S)
        for obj in begins:
            h = re.findall(r'(.*?)}', obj, re.S)
            if len(h) > 1:
                continue
            c = obj.replace(h[0]+"}", ' ')
            data_dict['%s' % (h[0])] = '%s' % (c)
            data = data.replace("\\begin{" + obj + "\\end", " ")

        return data_dict

    def get_author(self):
        author = re.findall(r'[Aa]uthor(s?){(.*?)}', self.tex_data, re.S)
        return author[0][1]

    def get_title(self):
        title = re.findall(r'[Tt]itle{(.*?)}', self.tex_data, re.S)
        return title[0]

    def get_ack(self):
        acknowledgments = re.findall(
            r'\\[Aa]cknowledgment(s?)(.*?)\\', self.tex_data, re.S)
        return acknowledgments[0][1]


class clean_data:
    """
    Contains functions to purge all unwanted elements from the tex file.
    """

    def __init__(self, tex_data):
        self.tex_data = tex_data

    def purge_images(self):
        """
        Purges images from the tex data using tag the '\begin{figure}'
        """
        imgs = re.findall(
            r'begin{figure}(.*?)end{figure}', self.tex_data, re.S)
        start = "\\begin{figure}"
        end = "end{figure}"
        imgs = [start + img + end for img in imgs]
        for img in imgs:
            self.tex_data = self.tex_data.replace(img, " ")

    def purge_tables(self):
        """
        Purges tables from the tex data using tag the '\begin{table}'
        """
        tables = re.findall(
            r'begin{table}(.*?)end{table}', self.tex_data, re.S)
        start = "\\begin{table}"
        end = "end{table}"
        tables = [start + table + end for table in tables]
        for table in tables:
            self.tex_data = self.tex_data.replace(table, " ")

    def purge_equations(self):
        """
        Purges equation from the tex data using tag the '\begin{equation}'
        """
        equations = re.findall(
            r'begin{equation}(.*?)end{equation}', self.tex_data, re.S)
        start = "\\begin{equation}"
        end = "end{equation}"
        equations = [start + equation + end for equation in equations]
        for equation in equations:
            self.tex_data = self.tex_data.replace(equation, " ")


# python get_details.py -p papers -o op_json.json

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="extract title,author,abstract,introduction,results,conclusions and acknowledgments from given set of research papers.")

    parser.add_argument("-parent", help="enter path to parent directory containing all research papers",
                        dest="parent_path", type=str, required=True)
    parser.add_argument("-output", help="enter path of output file",
                        dest="op", type=str, required=True)

    args = parser.parse_args()
    directory_path = args.parent_path
    op_file = args.op

    all_data = []

    all_files = [f for f in listdir(
        directory_path) if isfile(join(directory_path, f))]

    for tex_file in tqdm(all_files):

        p = os.path.join(directory_path, tex_file)

        with open(p, 'r', encoding='latin-1') as f:
            data_lst = f.readlines()
            data = ' '.join([str(elem) for elem in data_lst])
            cd = clean_data(data)
            cd.purge_images()
            cd.purge_tables()
            cd.purge_equations()

            ed = essential_data(cd.tex_data)
            d = {}
            d.update({"author": ed.get_author()})
            d.update({"title": ed.get_title()})
            d.update(ed.get_elements())
            d.update({"acknowledgement": ed.get_ack()})
            all_data.append(d)

            with open(op_file, "w") as outfile:
                json.dump(all_data, outfile, indent=4)
