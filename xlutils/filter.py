# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os
import xlrd,xlwt

from glob import glob

class BaseReader:

    def get_filepaths(self):
        """
        This is the most common method to implement. It must return an
        interable sequence of paths to excel files.
        """
        raise NotImplementedError

    def get_workbooks(self):
        """
        If the data to be processed is not stored in files or if
        special parameters need to be passed to xlrd.open_workbook
        then this method must be overriden.
        Any implementation must return an iterable sequence of tuples.
        The first element of which must be an xlrd.Book object and the
        second must be the filename of the file from which the book
        object came.
        """
        for path in self.get_filepaths():
            yield (
                xlrd.open_workbook(path, pickleable=0, formatting_info=1),
                os.path.split(path)[1]
                )

    def __call__(self,filter):
        """
        Once instantiated, a reader will be called and have the first
        filter in the chain passed. The implementation of this method
        should call the appropriate methods on the filter based on the
        cells found in the Book objects returned from the
        get_workbooks method.
        """
        for workbook,filename in self.get_workbooks():
            filter.workbook(workbook,filename)
            for sheet_x in range(workbook.nsheets):
                sheet = workbook.sheet_by_index(sheet_x)
                filter.sheet(sheet,sheet.name)
                for row_x in xrange(sheet.nrows):
                    filter.row(row_x,row_x)
                    for col_x in xrange(sheet.ncols):
                        filter.cell(row_x,col_x,row_x,col_x)
        filter.finish()
    
class BaseFilter:
    """
    This is a simple filter that just calls the next filter in the
    chain. The 'next' attribute is set up by the process method.
    It can make a good base class for a new filter.
    """

    def workbook(self,rdbook,wtbook_name):
        """
        The workbook method is called every time processing of a new
        workbook starts.

        rdbook - the xlrd.Book object from which the new workbook
                 should be created.

        wtbook_name - the name of the workbook into which content
                      should be written.
        """
        self.next.workbook(rdbook,wtbook_name)
   
    def sheet(self,rdsheet,wtsheet_name):
        """
        The sheet method is called every time processing of a new
        sheet in the current workbook starts.

        rdsheet - the xlrd.sheet.Sheet object from which the new
                  sheet should be created.

        wtsheet_name - the name of the sheet into which content
                       should be written.
        """
        self.next.sheet(rdsheet,wtsheet_name)
       
    def row(self,rdrowx,wtrowx):
        """
        The row method is called every time processing of a new
        row in the current sheet starts.
        It is primarily for copying row-based formatting from the
        source row to the target row.

        rdrowx - the index of the row in the current sheet from which
                 information for the row to be written should be
                 copied.

        wtrowx - the index of the row in sheet to be written to which
                 information should be written for the row being read.
        """
        self.next.row(rdrowx,wtrowx)

    def cell(self,rdrowx,rdcolx,wtrowx,wtcolx):
        """
        This is called for every cell in the sheet being processed.
        This is the most common method in which filtering and queuing
        of onward calls to the next filter takes place.

        rdrowx - the index of the row to be read from in the current
                 sheet. 

        rdcolx - the index of the column to be read from in the current
                 sheet. 

        wtrowx - the index of the row to be written to in the current
                 output sheet. 

        wtcolx - the index of the column to be written to in the current
                 output sheet. 
        """
        self.next.cell(rdrowx,rdcolx,wtrowx,wtcolx)

    def finish(self):
        """
        This method is called once processing of all workbooks has
        been completed.

        A filter should call this method on the next filter in the
        chain as an indication that no further calls will be made to
        any methods.
        """
        self.next.finish()

class BaseWriter:
    """
    This is the base writer that copies all data and formatting from
    the specified sources.
    It is designed for sequential use so when, for example, writing
    two workbooks, the calls must be ordered as follows:
    - workbook call for first workbook
    - sheet call for first sheet
    - row call for first row
    - cell call for left-most cell of first row
    - cell call for second-left-most cell of first row
    ...
    - row call for second row
    ...
    - sheet call for second sheet
    ...
    - workbook call for second workbook
    ...
    - finish call
    """
    
    wtbook = None
    
    def get_stream(self,filename):
        """
        This method is called once for each file written.
        The filename is passed and something with 'write' and 'close'
        methods that behave like a file object's must be returned.
        """
        raise NotImplementedError

    def close(self):
        if self.wtbook is not None:
            stream = self.get_stream(self.wtname)
            self.wtbook.save(stream)
            stream.close()

    def workbook(self,rdbook,wtbook_name):
        self.close()        
        self.rdbook = rdbook
        self.wtbook = xlwt.Workbook()
        self.wtname = wtbook_name
        self.style_list = []
        self.wtsheets = {}
        for rdxf in rdbook.xf_list:
            wtxf = xlwt.Style.XFStyle()
            #
            # number format
            #
            wtxf.num_format_str = rdbook.format_map[rdxf.format_key].format_str
            #
            # font
            #
            wtf = wtxf.font
            rdf = rdbook.font_list[rdxf.font_index]
            wtf.height = rdf.height
            wtf.italic = rdf.italic
            wtf.struck_out = rdf.struck_out
            wtf.outline = rdf.outline
            wtf.shadow = rdf.outline
            wtf.colour_index = rdf.colour_index
            wtf.bold = rdf.bold #### This attribute is redundant, should be driven by weight
            wtf._weight = rdf.weight #### Why "private"?
            wtf.escapement = rdf.escapement
            wtf.underline = rdf.underline_type #### 
            # wtf.???? = rdf.underline #### redundant attribute, set on the fly when writing
            wtf.family = rdf.family
            wtf.charset = rdf.character_set
            wtf.name = rdf.name
            # 
            # protection
            #
            wtp = wtxf.protection
            rdp = rdxf.protection
            wtp.cell_locked = rdp.cell_locked
            wtp.formula_hidden = rdp.formula_hidden
            #
            # border(s) (rename ????)
            #
            wtb = wtxf.borders
            rdb = rdxf.border
            wtb.left   = rdb.left_line_style
            wtb.right  = rdb.right_line_style
            wtb.top    = rdb.top_line_style
            wtb.bottom = rdb.bottom_line_style 
            wtb.diag   = rdb.diag_line_style
            wtb.left_colour   = rdb.left_colour_index 
            wtb.right_colour  = rdb.right_colour_index 
            wtb.top_colour    = rdb.top_colour_index
            wtb.bottom_colour = rdb.bottom_colour_index 
            wtb.diag_colour   = rdb.diag_colour_index 
            wtb.need_diag1 = rdb.diag_down
            wtb.need_diag2 = rdb.diag_up
            #
            # background / pattern (rename???)
            #
            wtpat = wtxf.pattern
            rdbg = rdxf.background
            wtpat.pattern = rdbg.fill_pattern
            wtpat.pattern_fore_colour = rdbg.pattern_colour_index
            wtpat.pattern_back_colour = rdbg.background_colour_index
            #
            # alignment
            #
            wta = wtxf.alignment
            rda = rdxf.alignment
            wta.horz = rda.hor_align
            wta.vert = rda.vert_align
            wta.dire = rda.text_direction
            # wta.orie # orientation doesn't occur in BIFF8! Superceded by rotation ("rota").
            wta.rota = rda.rotation
            wta.wrap = rda.text_wrapped
            wta.shri = rda.shrink_to_fit
            wta.inde = rda.indent_level
            # wta.merg = ????
            #
            self.style_list.append(wtxf)
   
    def sheet(self,rdsheet,wtsheet_name):
        self.rdsheet = rdsheet
        self.wtsheet_name=wtsheet_name
        self.wtsheet = wtsheet = self.wtbook.add_sheet(wtsheet_name)
        self.wtcols = set() # keep track of which columns have had their attributes set up
        self.wtrowx = -1 # assumes the output rows will be written in ascending order
        #
        # default column width: STANDARDWIDTH, DEFCOLWIDTH
        #
        if rdsheet.standardwidth is not None:
            # STANDARDWIDTH is expressed in units of 1/256 of a 
            # character-width, but DEFCOLWIDTH is expressed in units of
            # character-width; we lose precision by rounding to
            # the higher whole number of characters.
            #### XXXX TODO: implement STANDARDWIDTH record in xlwt.
            wtsheet.col_default_width = \
                (rdsheet.standardwidth + 255) // 256
        elif rdsheet.defcolwidth is not None:
            wtsheet.col_default_width = rdsheet.defcolwidth
        #
        # MERGEDCELLS
        # 
        mc_map = {}
        mc_nfa = set()
        for crange in rdsheet.merged_cells:
            rlo, rhi, clo, chi = crange
            mc_map[(rlo, clo)] = crange
            for rowx in xrange(rlo, rhi):
                for colx in xrange(clo, chi):
                    mc_nfa.add((rowx, colx))
        self.merged_cell_top_left_map = mc_map
        self.merged_cell_already_set = mc_nfa
        #
        # WINDOW2
        #
        wtsheet.show_formulas = rdsheet.show_formulas
        wtsheet.show_grid = rdsheet.show_grid_lines
        wtsheet.show_headers = rdsheet.show_sheet_headers
        wtsheet.panes_frozen = rdsheet.panes_are_frozen
        wtsheet.show_empty_as_zero = rdsheet.show_zero_values
        wtsheet.auto_colour_grid = rdsheet.automatic_grid_line_colour
        wtsheet.cols_right_to_left = rdsheet.columns_from_right_to_left
        wtsheet.show_outline = rdsheet.show_outline_symbols
        wtsheet.remove_splits = rdsheet.remove_splits_if_pane_freeze_is_removed
        wtsheet.selected = rdsheet.sheet_selected
        wtsheet.sheet_visible = rdsheet.sheet_visible
        wtsheet.page_preview = rdsheet.show_in_page_break_preview
        wtsheet.first_visible_row = rdsheet.first_visible_rowx
        wtsheet.first_visible_col = rdsheet.first_visible_colx
        wtsheet.grid_colour = rdsheet.gridline_colour_index
        wtsheet.preview_magn = rdsheet.cached_page_break_preview_mag_factor
        wtsheet.normal_magn = rdsheet.cached_normal_view_mag_factor
        #
        # DEFAULTROWHEIGHT
        #
        wtsheet.row_default_height =          rdsheet.default_row_height
        wtsheet.row_default_height_mismatch = rdsheet.default_row_height_mismatch
        wtsheet.row_default_hidden =          rdsheet.default_row_hidden
        wtsheet.row_default_space_above =     rdsheet.default_additional_space_above
        wtsheet.row_default_space_below =     rdsheet.default_additional_space_below
        #
        # BOUNDSHEET
        #
        wtsheet.visibility = rdsheet.visibility
       
    def row(self,rdrowx,wtrowx):
        self.wtrowx += 1
        wtrow = self.wtrow = self.wtsheet.row(self.wtrowx)
        # empty rows may not have a rowinfo record
        rdrow = self.rdsheet.rowinfo_map.get(rdrowx)
        if rdrow:
            wtrow.height = rdrow.height
            wtrow.has_default_height = rdrow.has_default_height
            wtrow.height_mismatch = rdrow.height_mismatch
            wtrow.level = rdrow.outline_level
            wtrow.collapse = rdrow.outline_group_starts_ends # No kiddin'
            wtrow.hidden = rdrow.hidden
            wtrow.space_above = rdrow.additional_space_above
            wtrow.space_below = rdrow.additional_space_below
            if rdrow.has_default_xf_index:
                wtrow.set_style(self.style_list[rdrow.xf_index])

    def cell(self,rdrowx,rdcolx,wtrowx,wtcolx):
        cell = self.rdsheet.cell(rdrowx,rdcolx)
        # setup column attributes if not already set
        if wtcolx not in self.wtcols and rdcolx in self.rdsheet.colinfo_map:
            rdcol = self.rdsheet.colinfo_map[rdcolx]
            wtcol = self.wtsheet.col(wtcolx)
            wtcol.width = rdcol.width
            wtcol.set_style(self.style_list[rdcol.xf_index])
            wtcol.hidden = rdcol.hidden
            wtcol.level = rdcol.outline_level
            wtcol.collapsed = rdcol.collapsed
            self.wtcols.add(wtcolx)
        # copy cell
        cty = cell.ctype
        if cty == xlrd.XL_CELL_EMPTY:
            return
        style = self.style_list[cell.xf_index]
        rdcoords2d = (rdrowx, rdcolx)
        if rdcoords2d in self.merged_cell_top_left_map:
            # The cell is the governing cell of a group of 
            # merged cells.
            rlo, rhi, clo, chi = self.merged_cell_top_left_map[rdcoords2d]
            assert (rlo, clo) == rdcoords2d
            self.wtsheet.write_merge(
                self.wtrowx, self.wtrowx + rhi - rlo - 1,
                wtcolx, wtcolx + chi - clo - 1, 
                cell.value, style)
            return
        if rdcoords2d in self.merged_cell_already_set:
            # The cell is in a group of merged cells.
            # It has been handled by the write_merge() call above.
            # We avoid writing a record again because:
            # (1) It's a waste of CPU time and disk space.
            # (2) xlwt does not (as at 2007-01-12) ensure that only
            # the last record is written to the file.
            # (3) If you write a data record for a cell
            # followed by a blank record for the same cell,
            # Excel will display a blank but OOo Calc and
            # Gnumeric will display the data :-(
            return
        if cty == xlrd.XL_CELL_TEXT:
            self.wtrow.set_cell_text(wtcolx, cell.value, style)
        elif cty == xlrd.XL_CELL_NUMBER or cty == xlrd.XL_CELL_DATE:
            self.wtrow.set_cell_number(wtcolx, cell.value, style)
        elif cty == xlrd.XL_CELL_BLANK:
            self.wtrow.set_cell_blank(wtcolx, style)
        elif cty == xlrd.XL_CELL_BOOLEAN:
            self.wtrow.set_cell_boolean(wtcolx, cell.value, style)
        elif cty == error_type:
            self.wtrow.set_cell_error(wtcolx, cell.value, style)
        else:
            raise Exception(
                "Unknown xlrd cell type %r with value %r at (shx=%r,rowx=%r,colx=%r)" \
                % (cty, value, sheetx, rowx, colx)
                )

    def finish(self):
        self.close()

    
class GlobReader(BaseReader):

    def __init__(self,spec):
        self.spec = spec
        
    def get_filepaths(self):
        return glob(self.spec)

class DirectoryWriter(BaseWriter):

    def __init__(self,path):
        self.dir_path = path
        
    def get_stream(self,filename):
        return file(os.path.join(self.dir_path,filename),'wb')

class MethodFilter:
    """
    This is a base class that implements functionality for filters
    that want to do a common task such as logging, printing or memory
    usage recording on certain calls.
    """

    def __init__(self,call_on=(
        'workbook',
        'sheet',
        'row',
        'cell',
        'finish',
        )):
        self.call_on = call_on

    def __getattr__(self,name):
        pass
        
def process(reader,*chain):
    for i in range(len(chain)-1):
        chain[i].next = chain[i+1]
    reader(chain[0])