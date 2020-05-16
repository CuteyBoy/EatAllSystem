import os
import concurrent.futures
from data.remote.download.AbsDownload import AbsDownload


class PDFDownload(AbsDownload):
    """
    DDF文件的下载
    """

    def __init__(self):
        from data.database.table.StockFrTable import StockFrTable
        super().__init__(StockFrTable())

    def _get_url(self, **kwargs):
        return kwargs.get("pdf_path")

    def _get_headers(self, **kwargs):
        return None

    def _get_params(self, **kwargs):
        return None

    @classmethod
    def _create_dir(cls, dir_name):
        """
        创建目录，如果目录没有存在
        :param dir_name:
        :return:
        """
        dir_path = os.path.join(os.getcwd(), dir_name)
        if os.path.exists(dir_path) is False:
            os.mkdir(dir_path)

    def download_to_db(self, **kwargs):
        from data.database.table.StockTable import AllStockTable
        all_stock_table = AllStockTable()
        all_stock_list = all_stock_table.find()
        all_stock_size = all_stock_list.count()
        print("all_size=", all_stock_size)
        index = 0
        if all_stock_size > 0:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                to_do = list()
                for stock in all_stock_list:
                    code = stock["code"]
                    future = executor.submit(self._start_download, code)
                    to_do.append(future)
                    index += 1
                    print("downloaded save %s/%s" % (index, all_stock_size))
                for future in concurrent.futures.as_completed(to_do):
                    future.result()

    def _start_download(self, code):
        fr_data_list = self.table.find({"code": code})
        print("current download code=%s size=%s" % (code, fr_data_list.count()))
        if fr_data_list.count() > 0:
            for fr in fr_data_list:
                title = str(fr["title"])
                year = title.split("：")[-1].split("年")[0]
                path_url = str(fr["pdf_path"])
                suffix_name = path_url.split("/")[-1]
                pdf_dir = "dpf"
                self._create_dir(pdf_dir)
                save_dir = "%s/s%s" % (pdf_dir, code)
                self._create_dir(save_dir)
                file_path_name = "%s/%s_%s" % (save_dir, year, suffix_name)
                save_file_path = os.path.join(os.getcwd(), file_path_name)
                if os.path.exists(save_file_path):
                    continue
                self.table.update_one({"_id": fr["_id"]}, {"$set": {"local_pdf_path": save_file_path}})
                with self.get_request_result(pdf_path=path_url, stream=True) as pdf:
                    with open(save_file_path, 'wb') as stock_file:
                        stock_file.write(pdf.content)
                        print("%s save end; path is %s" % (code, save_file_path))
