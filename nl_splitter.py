#@title Life name mapper
import fitz  # PyMuPDF
import json
import os
from PyPDF2 import PdfReader, PdfWriter

def is_exist(l_name,li_list):
  for topic in li_list:
    if l_name==topic["topic"]:
      # print(l_name,topic)
      return True

  return False

def get_nl_name(text,prev_li_num=None):
  with open('nl.json', 'r') as file:
    map_data = json.load(file)
  for l in map_data:
    text=text.lower()
    text=text.replace(" ","").replace("-","")
    text=text.replace("\n","")
    match_count=0
    exclude_match_flag=False
    for w in l["include"]:
      if w.lower() in text:
        match_count+=1
    for exw in l["exclude"]:
      if exw.lower() in text:
        exclude_match_flag=True
    if match_count==len(l["include"]) and not exclude_match_flag:
      if not is_exist(l["name"],li_list=prev_li_num):
        return l["name"]

def check_start_page(text):
  text=text.lower()
  text=text.replace(" ","").replace("-","")
  text=text.replace("\n","")
  if len(text)<300:
    return False
  if "nl1" in text.lower() and "nl2" not in text.lower():

    return True
  elif "particular" in text.lower() or "total" in text.lower():
    return True
  else:
    return False

def get_nl_toc(pdf_path):
    doc = fitz.open(pdf_path)
    nl_toc = []
    start_flag=False
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        rect = page.rect  # Get the full page rectangle
        upper_half = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1 / 2)  # Define upper half

        # Extract text blocks with their coordinates
        blocks = page.get_text("blocks")

        # Sort blocks by vertical position (y0), then horizontal (x0)
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        text=""
        for block in blocks:
            text =text+block[4]


        if not start_flag:
          if check_start_page(text):
            l_num=1
            nl_toc.append({
              "topic":"NL-1",
              "page":page_num
          })
            start_flag=True
            continue
        if not start_flag:
          continue
        text=text[:500]
        if page_num==6:
          print(text)

        if len(nl_toc)!=0:
          prev_li_num=int(nl_toc[-1]["topic"].split("-")[1])
          l_name=get_nl_name(text,nl_toc)
        else:
          l_name=get_nl_name(text)

        try:
          l_num=int(l_name.split("-")[1])
        except:
          continue

        if len(nl_toc)==0:
          nl_toc.append({
              "topic":l_name,
              "page":page_num
          })
        elif l_name is not None and nl_toc[-1]["topic"]!=l_name and l_num>int(nl_toc[-1]["topic"].split("-")[1]):
          nl_toc.append({
              "topic":l_name,
              "page":page_num
          })

    return nl_toc
