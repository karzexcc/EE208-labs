# SJTU EE208

import sys, os, lucene

from java.io import File
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, BooleanQuery
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanClause

def parse_command(command: str) -> dict:
    '''
        convert a command string into a dictionary.
        example:
            input: 'rust site:blog.csdn.net'
            output: {'contents': 'rust','site': 'blog.csdn.net'}
    '''
    allow_opt = set(['title', 'url', 'author', 'id', 'source', 'photography', 'imgaddr']) # 合法的关键词
    command_dict = {}
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2] # 分成关键词和value两个部分
            opt = opt.lower() # 将输入的关键词全部转换为小写
            if opt in allow_opt and value != '':
                # 如关键词合法，将:后的值加入字典
                # 忽略非法关键词
                command_dict[opt] = command_dict.get(opt, '') + ' ' + value
        else:
            # 不带:的内容，应当是contents之中的
            command_dict['contents'] = command_dict.get('contents', '') + ' ' + i

    for k, _ in command_dict.items():
        command_dict[k] = command_dict[k][1:] # 去除前缀的空格
    return command_dict

def run(searcher, analyzer):
    '''
        Repeatedly get the results correspoing to the 
    '''
    # while True:
    print()
    print ("Hit enter with no input to quit.")
    # command = raw_input("Query:")
    # command = unicode(command, 'GBK')

    while True:
        command = input("please input the query: ")
        if not command:
            break
        limit = int(input("please input the maximum retrieval file number: "))


        print()
        print ("Searching for:", command)
        command_dict = parse_command(command)
        print(command_dict)
        querys = BooleanQuery.Builder()
        for key, value in command_dict.items():
            query = QueryParser(key, analyzer).parse(value)
            querys.add(query, BooleanClause.Occur.MUST)
        # parse the query and get the results.
        scoreDocs = searcher.search(querys.build(), int(limit)).scoreDocs
        
        print ("%s total matching documents." % len(scoreDocs))

        for i, scoreDoc in enumerate(scoreDocs):
            # read the title, path, name site, and url from the results,
            # and print them in the terminal.
            # besides, print the content in result_content\_.txt
            doc = searcher.doc(scoreDoc.doc)

            title, url, author, pid, source, photography, imgaddr = \
				doc.get("title"), doc.get("url"), doc.get("author"), doc.get('id'), doc.get('source'), doc.get('photography'), doc.get('imgaddr')


            print(f'{i + 1}:, \n' +
				f'id: {pid} \n' +
                f'title: {title} \n' + 
                f'author: {author} \n' + 
                f'photography: {photography} \n' +
				f'source: {source} \n' + 
                f'url: {url}' + 
                f'imgaddr: {imgaddr} \n' + 
                f'score: {scoreDoc.score}')   # write to file


if __name__ == '__main__':

    STORE_DIR = "pic_index"
    #initialize.
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print ('lucene', lucene.VERSION)
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = CJKAnalyzer()#Version.LUCENE_CURRENT)
    run(searcher, analyzer)
    del searcher