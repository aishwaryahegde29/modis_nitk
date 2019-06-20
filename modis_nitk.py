# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MODISNITK
                                 A QGIS plugin
 Plugin to process modis data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-12-31
        git sha              : $Format:%H$
        copyright            : (C) 2018 by NITK
        email                : aishwaryahegde29@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog
from qgis.PyQt.QtWidgets import *
# Initialize Qt resources from file resources.py
from nltk import infile
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox, QProgressBar
from qgis.PyQt.QtCore import *


from .resources import *
# Import the code for the dialog
from pyhdf.SD import SD, SDC
from osgeo import gdal
from .modis_nitk_dialog import MODISNITKDialog
import os.path
import processing, os, subprocess, time
from qgis.utils import *
from qgis.core import *
from qgis.gui import QgsMessageBar
# from qgis.PyQt.QtGui import QProgressBar
from qgis.PyQt.QtCore import *
from pandas import read_csv

import processing
import gdal
import os.path
import os, sys, time, gdal
from gdalconst import *
import glob
import csv
from pymodis import convertmodis_gdal
from subprocess import call
import pandas
from qgis.utils import *
from qgis.core import *
from qgis.gui import QgsMessageBar
from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()

import glob, os, os.path


# from qgis.PyQt.QtGui import QProgressBar

class MODISNITK:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname ( __file__ )
        # initialize locale
        locale = QSettings ().value ( 'locale/userLocale' )[0:2]
        locale_path = os.path.join (
            self.plugin_dir,
            'i18n',
            'MODISNITK_{}.qm'.format ( locale ) )

        if os.path.exists ( locale_path ):
            self.translator = QTranslator ()
            self.translator.load ( locale_path )

            if qVersion () > '4.3.3':
                QCoreApplication.installTranslator ( self.translator )

        # Create the dialog (after translation) and keep reference
        self.dlg = MODISNITKDialog ()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr ( u'&MODIS_NITK' )
        self.toolbar = self.iface.addToolBar ( u'MODISNITK' )
        self.toolbar.setObjectName ( u'MODISNITK' )

        self.dlg.lineEdit.textChanged.connect ( self.scldisplay )
        self.dlg.lineEdit.textChanged.connect ( self.showlayers )
        self.dlg.lineEdit.textChanged.connect ( self.conversion )
        self.dlg.lineEdit_out.textChanged.connect ( self.conversion )
        self.dlg.startprocessing.clicked.connect ( self.conversion )
        self.dlg.projection.setCrs ( QgsCoordinateReferenceSystem () )
        self.dlg.projection.crsChanged.connect ( self.proj )
        self.dlg.checkBoxclip.clicked.connect ( self.clipsh )
        self.dlg.scalefactor.clicked.connect ( self.sclfactor )
        self.dlg.sfactor.textChanged.connect ( self.sclfactor )
        self.dlg.checkBox_single.clicked.connect ( self.tsaprocessing_s )
        self.dlg.checkBox_multiple.clicked.connect ( self.tsaprocessing_m )
        self.dlg.pb_cancel.clicked.connect(self.Pb_cancel)
        self.dlg.pb_cancel_tsa.clicked.connect(self.cancel_tsa)
        self.dlg.checkBox_g.clicked.connect(self.newformat_s)
        self.dlg.checkBox_g_m.clicked.connect ( self.newformat )

        self.dlg.radioButton_LINE.clicked.connect(self.graphplot_s_line)
        self.dlg.radioButton_BAR.clicked.connect(self.graphplot_s_bar)
        self.dlg.radioButton_POINT.clicked.connect(self.graphplot_s_point)
        self.dlg.radioButton_LINE_m.clicked.connect(self.graphplot_m_line)
        self.dlg.radioButton_POINT_m.clicked.connect(self.graphplot_m_point)
        self.dlg.radioButton_BAR_m.clicked.connect(self.graphplot_m_bar)



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate ( 'MODISNITK', message )

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon ( icon_path )
        action = QAction ( icon, text, parent )
        action.triggered.connect ( callback )
        action.setEnabled ( enabled_flag )

        if status_tip is not None:
            action.setStatusTip ( status_tip )

        if whats_this is not None:
            action.setWhatsThis ( whats_this )

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon ( action )

        if add_to_menu:
            self.iface.addPluginToMenu (
                self.menu,
                action )

        self.actions.append ( action )

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/modis_nitk/icon.png'
        self.add_action (
            icon_path,
            text=self.tr ( u'MODIS_NITK' ),
            callback=self.run,
            parent=self.iface.mainWindow () )
        self.dlg.lineEdit.clear ()
        self.initFolder ();
        self.dlg.hdfbrowse.clicked.connect ( self.openhdf )

        self.dlg.lineEdit_out.clear ()
        self.outFolder ();
        self.dlg.outbrowse.clicked.connect ( self.outputloc )

        self.newoutFolder ();
        self.dlg.outbrowse.clicked.connect ( self.createfolder)

        self.shFolder ();
        self.dlg.browseshapedfile.clicked.connect ( self.browsesh)

        self.tsafolder ();
        self.dlg.pushButton_tsa.clicked.connect ( self.browsetsa)

        self.csvfolder ();
        self.dlg.pushButton_csv.clicked.connect ( self.browsescv)

        self.tsaoutput ();
        self.dlg.toolButton_tsa_out.clicked.connect ( self.tsaoutputloc)

        self.newcsvfl ();
        self.dlg.toolButton_tsa_out.clicked.connect ( self.createcsv)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu (
                self.tr ( u'&MODIS_NITK' ),
                action )
            self.iface.removeToolBarIcon ( action )
        del self.toolbar

    def initFolder(self):
        path_project = QgsProject.instance ().fileName ()
        path_project = path_project[:path_project.rfind ( "/" ):]

        self.folderName = path_project

        self.dlg.lineEdit.setText ( self.folderName );

    def openhdf(self):
        infile = str ( QFileDialog.getOpenFileName ( caption="Input HDF file",
                                                     filter="hdf(*.hdf)" )[0] )
        if infile != "":
            self.folderName = infile
        self.dlg.lineEdit.setText ( self.folderName );

    def scldisplay(self):
        self.dlg.lineEdit.setText ( self.folderName )
        logger = self.dlg.display
        logger.append ( '\n' )
        if 'MOD11' in self.folderName:
            logger = self.dlg.display
            logger.append ( 'The input MODIS Product is MOD11,scale factors for SDS layers are:\n'
                            'LST_Day_1km-------> 0.02\n'
                            'QC_Day-------------> NA\n'
                            'Day_view_time-----> 0.1\n'
                            'Day_view_angl-----> NA\n'
                            'LST_Night_1km-----> 0.02\n'
                            'QC_Night-----------> NA\n'
                            'Night_view_time---> 0.1\n'
                            'Night_view_angl---> NA\n'
                            'Emis_31------------> 0.02\n'
                            'Emis_32------------> 0.02\n'
                            'Clear_day_cov----> 0.0005\n'
                            'Clear_night_cov--> 0.0005\n' )
        if 'MOD16' in self.folderName:
            logger = self.dlg.display
            logger.append ( 'The input MODIS Product is MOD16,scale factors for SDS layers are:\n'
                            'ET_500m-----> 0.1\n'
                            'LE_500m-----> 10000\n'
                            'PET_500m----> 0.1\n'
                            'PLE_500m----> 10000\n'
                            'ET_QC_500m-> NA\n' )
        if 'MOD09' in self.folderName:
            logger = self.dlg.display
            logger.append ( 'The input MODIS Product is MOD09,scale factors for SDS layers are:\n'
                            'sur_refl_b01----------> 0.0001\n'
                            'sur_refl_b02----------> 0.0001\n'
                            'sur_refl_b03----------> 0.0001\n'
                            'sur_refl_b04----------> 0.0001\n'
                            'sur_refl_b05----------> 0.0001\n'
                            'sur_refl_b06----------> 0.0001\n'
                            'sur_refl_b07----------> 0.0001\n'
                            'sur_refl_qc_500m-----> NA     \n'
                            'sur_refl_szen----------> 0.01   \n'
                            'sur_refl_vzen----------> 0.01   \n'
                            'sur_refl_raz------------> 0.01   \n'
                            'sur_refl_state_500m--> NA    \n'
                            'sur_refl_state_500m--> NA    \n' )
        if 'MCD15' in self.folderName:
            logger = self.dlg.display
            logger.append ( 'The input MODIS Product is MCD15 ,scale factors for SDS layers are:\n'
                            'Fpar_500m -----------> 0.01\n'
                            'Lai_500m  -----------> 0.1\n'
                            'FparLai_QC ----------> NA\n'
                            'FparExtra_QC --------> NA\n'
                            'FparStdDev_500m -----> 0.01\n'
                            'LaiStdDev_500m-------> 0.1\n')
        if 'MOD17' in self.folderName:
            logger = self.dlg.display
            logger.append ( 'The input MODIS Product is MOD17 ,scale factors for SDS layers are:\n'
                            'Gpp_500m ------------>0.0001\n'
                            'PsnNet_500m --------->0.0001\n'
                            'Psn_QC_500m --------->NA\n')

        if 'MOD17' in self.folderName:
            logger = self.dlg.display
            logger.append('The input MODIS Product is MOD17 ,scale factors for SDS layers are:\n'
                          'Gpp_500m ------------>0.0001\n'
                          'PsnNet_500m --------->0.0001\n'
                          'Psn_QC_500m --------->NA\n')

        if 'MOD44' in self.folderName:
            logger = self.dlg.display
            logger.append('The input MODIS Product is MOD44 ,scale factors for SDS layers are:\n'
                          'Percent_Tree_Cover ------------->NA\n'
                          'Percent_NonTree_Vegetation------>NA\n'
                          'Percent_NonVegetated------------>NA\n'
                          'Quality ------------------------>NA\n'
                          'Percent_Tree_Cover_SD ---------->0.01\n'
                          'Percent_NonVegetated_SD -------->0.01\n'
                          'Cloud--------------------------->NA\n')



    def showlayers(self):
        self.dlg.cmblayers.selectAllOptions ()
        self.dlg.lineEdit.setText ( self.folderName )
        file = SD ( self.folderName, SDC.READ )
        datasets_dic = file.datasets ()
        lay = []
        for idx, sds in enumerate ( datasets_dic.keys () ):
            k = ((idx, sds)[1])
            lay.append ( str ( k ) )
        self.itemsindropdownmenu = lay
        self.dlg.cmblayers.addItems ( lay )

    def outFolder(self):
        out_path_project = QgsProject.instance ().fileName ()
        out_path_project = out_path_project[:out_path_project.rfind ( "/" ):]

        self.outfolderName = out_path_project

    def outputloc(self):
        ofile = QFileDialog.getExistingDirectory ( self.dlg, caption=" Output File " )

        self.outfolderName = ofile + "/"

    def newoutFolder(self):
        new_path_project = QgsProject.instance ().fileName ()
        new_path_project = new_path_project[:new_path_project.rfind ( "/" ):]

        self.newfolderName = new_path_project

    def createfolder(self):
        self.dlg.lineEdit_out.setText ( self.outfolderName )
        folderx01 = self.outfolderName + (
                    'MODIS-DIR_%s' % (time.strftime ( "%Y%m%d_" )) + time.strftime ( "%H%M%S" ) + "/")
        if not os.path.exists ( folderx01 ):
            os.mkdir ( folderx01 )
        self.newfolderName = folderx01
        self.dlg.lineEdit_out.setText ( self.newfolderName )

    def conversion(self):
        self.dlg.lineEdit.setText ( self.folderName )
        self.dlg.lineEdit_out.setText ( self.newfolderName )
        subset = []
        check = self.dlg.cmblayers.checkedItems ()
        for i in self.itemsindropdownmenu:
            if i in check:
                subset.append ( 1 )
            else:
                subset.append ( 0 )
        subset = [1 if i in check else 0 for i in self.itemsindropdownmenu]
        hdffile = self.folderName
        prefix = self.newfolderName
        outformat = 'Gtiff'
        res = 1200
        epsg = 32647
        wkt = None
        resampl = 'NEAREST_NEIGHBOR'
        vrt = False
        convert = convertmodis_gdal.convertModisGDAL ( hdffile, prefix, subset, res, outformat, epsg, wkt, resampl,
                                                       vrt )
        convert.run ()

    def proj(self):
        self.dlg.startprocessing.clicked.connect ( self.proj )
        self.dlg.startprocessing.clicked.connect ( self.deloldfile )
        self.dlg.lineEdit_out.setText ( self.newfolderName )
        ppath = self.newfolderName
        os.chdir ( ppath )
        for file in glob.glob ( "*.tif" ):
            inputw = gdal.Open ( file )
            filename, ext = os.path.splitext ( file )
            out = ("r" + filename + ext)
            out_loc = (ppath + out)
            gdal.Warp ( out_loc, inputw, dstSRS='EPSG:4326' )

    def deloldfile(self):
        self.dlg.lineEdit_out.setText ( self.newfolderName )
        path = self.newfolderName
        for fname in glob.glob ( path + "_*" ):
            os.remove ( fname )

    def shFolder(self):
        sh_path_project = QgsProject.instance ().fileName ()
        sh_path_project = sh_path_project[:sh_path_project.rfind ( "/" ):]

        self.shfolderName = sh_path_project

    def browsesh(self):
        shfile = str ( QFileDialog.getOpenFileName ( caption="Select Shapefile",
                                                     filter="shp(*.shp)" )[0] )
        if shfile != "":
            self.shfolderName = shfile
        self.shfolderName = shfile

    def clipsh(self):
        self.dlg.startprocessing.clicked.connect ( self.clipsh )
        self.dlg.startprocessing.clicked.connect ( self.deloldfileclip )
        self.dlg.lineEdit_out.setText ( self.newfolderName )
        path_sh = self.newfolderName
        os.chdir ( path_sh )
        for ifile in glob.glob ( "*.tif" ):
            filenames, extn = os.path.splitext ( ifile )
            outp = ("clip_" + filenames + extn)
            output_tif = (path_sh + outp)
            s_file = self.shfolderName
            raster_layer = QgsRasterLayer ( ifile, 'raster' )
            mask_layer = QgsVectorLayer ( s_file, 'mask', 'ogr' )
            processing.run ( "gdal:cliprasterbymasklayer",
                             {"INPUT": raster_layer,
                              "MASK": mask_layer,
                              "CROP_TO_CUTLINE": False,
                              "OPTIONS": 'COMPRESS=LZW',
                              "OUTPUT": output_tif} )

    def deloldfileclip(self):
        self.dlg.lineEdit_out.setText ( self.newfolderName )
        dpath = self.newfolderName
        for filenm in glob.glob ( dpath + "_*" ):
            os.remove ( filenm )
        for filenm in glob.glob ( dpath + "r*" ):
            os.remove ( filenm )

    def sclfactor(self):
        self.dlg.startprocessing.clicked.connect ( self.sclfactor )
        self.dlg.startprocessing.clicked.connect ( self.delfilescale )
        self.dlg.lineEdit_out.setText ( self.newfolderName )
        sf_path = self.newfolderName
        os.chdir ( sf_path )
        for sffile in glob.glob ( "*.tif" ):
            filname, exten = os.path.splitext ( sffile )
            outpt = ("sf_" + filname + exten)
            sf_out = (sf_path + outpt)
            entries = []
            myLayer1 = QgsRasterLayer ( sffile, 'raster' )
            my1 = QgsRasterCalculatorEntry ()
            my1.ref = 'my@1'
            my1.raster = myLayer1
            my1.bandNumber = 1
            entries.append ( my1 )
            SF = self.dlg.sfactor.text ()
            calc = QgsRasterCalculator ( 'my@1*{}'.format ( SF ),
                                         sf_out,
                                         'GTiff',
                                         myLayer1.extent (),
                                         myLayer1.width (),
                                         myLayer1.height (),
                                         entries )

            calc.processCalculation ()

    def delfilescale(self):
        self.dlg.lineEdit_out.setText ( self.newfolderName )
        pathd = self.newfolderName
        for filenam in glob.glob ( pathd + "_*" ):
            os.remove ( filenam )
        for filenam in glob.glob ( pathd + "r*" ):
            os.remove ( filenam )
        for filenam in glob.glob ( pathd + "clip*" ):
            os.remove ( filenam )
        for filenam in glob.glob ( pathd + "sf_sf_*" ):
            os.remove ( filenam )

    def Pb_cancel(self):
        self.dlg.lineEdit.clear()
        self.dlg.lineEdit_out.clear()
        self.dlg.sfactor.clear()

    def cancel_tsa(self):
        self.dlg.lineEdit_tsa.clear()
        self.dlg.lineEdit_tsa_out.clear()
        self.dlg.lineEdit_xcord.clear()
        self.dlg.lineEdit_ycord.clear()
        self.dlg.lineEdit_csv.clear()


    def tsafolder(self):
        inptsa_path_project = QgsProject.instance ().fileName ()
        inptsa_path_project = inptsa_path_project[:inptsa_path_project.rfind ( "/" ):]

        self.inptsafolderName = inptsa_path_project
        self.dlg.lineEdit_tsa.setText ( self.inptsafolderName );

    def browsetsa(self):
        i_t_file = QFileDialog.getExistingDirectory ( self.dlg, caption="Select Folder having .tif file" )
        self.inptsafolderName = i_t_file + "/"
        self.dlg.lineEdit_tsa.setText ( self.inptsafolderName );

    def csvfolder(self):
        csv_path_project = QgsProject.instance ().fileName ()
        csv_path_project = csv_path_project[:csv_path_project.rfind ( "/" ):]

        self.csvfolderName = csv_path_project
        self.dlg.lineEdit_csv.setText ( self.csvfolderName );

    def browsescv(self):
        cfile = str ( QFileDialog.getOpenFileName ( caption="Select point shape file",
                                                    filter="SHP(*.shp)" )[0] )
        if cfile != "":
            self.csvfolderName = cfile
        self.csvfolderName = cfile
        self.dlg.lineEdit_csv.setText ( self.csvfolderName );

    def tsaoutput(self):
        tsaoutput_path_project = QgsProject.instance ().fileName ()
        tsaoutput_path_project = tsaoutput_path_project[:tsaoutput_path_project.rfind ( "/" ):]

        self.tsaoutfolderName = tsaoutput_path_project

    def tsaoutputloc(self):
        outtsafile = QFileDialog.getExistingDirectory ( self.dlg, caption="Select Folder for output data" )
        self.tsaoutfolderName = outtsafile + "/"

    def newcsvfl(self):
        newcsv_path_project = QgsProject.instance ().fileName ()
        newcsv_path_project = newcsv_path_project[:newcsv_path_project.rfind ( "/" ):]

        self.newcsvName = newcsv_path_project

    def createcsv(self):
        self.dlg.lineEdit_tsa_out.setText ( self.tsaoutfolderName )
        folderx02 = self.tsaoutfolderName + (
                    'tsa_%s' % (time.strftime ( "%Y%m%d_" )) + time.strftime ( "%H%M%S" ) + ".csv")
        with open ( os.path.join ( folderx02 ), 'w' ):
            self.newcsvName = folderx02
        self.dlg.lineEdit_tsa_out.setText ( self.newcsvName )

    def tsaprocessing_s(self):
        self.dlg.tsabuttonBox_m.clicked.connect(self.tsaprocessing_s)
        self.dlg.lineEdit_tsa.setText ( self.inptsafolderName )
        self.dlg.lineEdit_tsa_out.setText ( self.newcsvName )
        self.dlg.lineEdit_csv.setText ( self.csvfolderName )
        tiffolder = self.inptsafolderName
        os.chdir ( tiffolder )
        gdal.AllRegister()
        for flle in glob.glob ( "*.tif" ):
            nome, enx = os.path.splitext ( flle )
            ds = gdal.Open ( flle, GA_ReadOnly )
            # get georeference info
            transform = ds.GetGeoTransform ()
            xOrigin = transform[0]
            yOrigin = transform[3]
            pixelWidth = transform[1]
            pixelHeight = transform[5]
            # loop through the coordinates
            xv = self.dlg.lineEdit_xcord.text ()
            yv = self.dlg.lineEdit_ycord.text ()
            xValues = [float ( x ) for x in xv.split ()]
            yValues = [float ( x ) for x in yv.split ()]
            for xValue, yValue in zip ( xValues, yValues ):
                x = xValue
                y = yValue
                # compute pixel offset
                xOffset = float ( (x - xOrigin) / pixelWidth )
                yOffset = float ( (y - yOrigin) / pixelHeight )
                # create a string to print out
                s = "%s  %s " % (x, y)
                data = ds.ReadAsArray ( xOffset, yOffset, 1, 1 )
                value = data[0, 0]
                s = "%s%s%s " % (nome, ",", value)
                # print out the data string
                panth = self.newcsvName
                with open ( panth, 'a' ) as file:
                    file.write ( s )
                    file.write ( '\n' )

    def newformat_s(self):
        self.dlg.lineEdit_csv.setText ( self.csvfolderName )
        hj= self.newcsvName
        with open ( hj, newline='' ) as f:
            r = csv.reader ( f )
            data = [line for line in r]
        with open ( hj, 'w', newline='' ) as f:
            w = csv.writer ( f )
            w.writerow ( ['Filename','PixelValue'] )
            w.writerows ( data )


    def graphplot_s_line(self):
        self.dlg.checkBox_single.clicked.connect(self.graphplot_s_line)
        self.dlg.tsabuttonBox_m.clicked.connect(self.graphplot_s_line)
        self.dlg.lineEdit_tsa.setText ( self.inptsafolderName )
        self.dlg.lineEdit_tsa_out.setText ( self.newcsvName )
        self.dlg.lineEdit_csv.setText ( self.csvfolderName )
        hul = self.newcsvName
        ddd = pd.read_csv ( hul)
        yk = ddd.columns[1:]
        plt.plot ( ddd['Filename'], ddd['PixelValue'],marker='o' )
        plt.xlabel ( 'Raster file Name' )
        plt.ylabel ( 'Pixel Value' )
        plt.title ( 'Graphical Representation of variation in pixel value' )
        plt.legend ( yk )
        plt.xticks ( ddd['Filename'], rotation=90 )
        plt.grid ( True )
        plt.show ()


    def graphplot_s_bar(self):
        self.dlg.checkBox_single.clicked.connect(self.graphplot_s_line)
        self.dlg.tsabuttonBox_m.clicked.connect(self.graphplot_s_bar)
        self.dlg.lineEdit_tsa.setText(self.inptsafolderName)
        self.dlg.lineEdit_tsa_out.setText ( self.newcsvName )
        self.dlg.lineEdit_csv.setText ( self.csvfolderName )
        juk = self.newcsvName
        dko = pd.read_csv ( juk )
        yi = dko.columns[1:]
        plt.bar( dko['Filename'], dko['PixelValue'], align='center',color='white', edgecolor='black', hatch='//')
        plt.xlabel ( 'Raster file Name' )
        plt.ylabel ( 'Pixel Value' )
        plt.title ( 'Graphical Representation of variation in pixel value' )
        plt.legend ( yi )
        plt.xticks ( dko['Filename'], rotation=90 )
        plt.show ()

    def graphplot_s_point(self):
        self.dlg.checkBox_single.clicked.connect(self.graphplot_s_point)
        self.dlg.tsabuttonBox_m.clicked.connect(self.graphplot_s_point)
        self.dlg.lineEdit_tsa.setText(self.inptsafolderName)
        self.dlg.lineEdit_tsa_out.setText ( self.newcsvName )
        self.dlg.lineEdit_csv.setText ( self.csvfolderName )
        juk = self.newcsvName
        dko = pd.read_csv ( juk )
        yi = dko.columns[1:]
        plt.scatter( dko['Filename'], dko['PixelValue'])
        plt.xlabel ( 'Raster file Name' )
        plt.ylabel ( 'Pixel Value' )
        plt.title ( 'Graphical Representation of variation in pixel value' )
        plt.legend ( yi )
        plt.xticks ( dko['Filename'], rotation=90 )
        plt.grid ( True )
        plt.show ()

    def tsaprocessing_m(self):
        self.dlg.tsabuttonBox_m.clicked.connect(self.tsaprocessing_m)
        self.dlg.lineEdit_tsa.setText ( self.inptsafolderName )
        self.dlg.lineEdit_tsa_out.setText ( self.tsaoutfolderName )
        self.dlg.lineEdit_csv.setText ( self.csvfolderName )
        inptif_folder = self.inptsafolderName
        os.chdir ( inptif_folder )
        gdal.AllRegister ()
        for fle in glob.glob ( "*.tif" ):
            nme, ex = os.path.splitext ( fle )
            cvfle = self.csvfolderName
            rast = QgsRasterLayer ( fle, 'raster' )
            pointlayer = QgsVectorLayer ( cvfle, 'ogr' )
            rprovider = rast.dataProvider ()
            points = [feat.geometry ().asPoint () for feat in pointlayer.getFeatures ()]
            val = [rprovider.identify ( point, QgsRaster.IdentifyFormatValue ).results () for point in points]
            for i, point in enumerate ( points ):
                fomo = val[i].values ()
                jomo = (float ( [x for x in fomo][0] ))
                s = "%s%s%s%s%s" % (nme, ",",'Station{}'.format(i+1), ",", jomo)
                pathn = self.newcsvName
                with open ( pathn, 'a' ) as file:
                    file.write ( s )
                    file.write ( '\n' )


    def newformat(self):
        self.dlg.lineEdit_tsa_out.setText ( self.tsaoutfolderName )
        dfg = self.newcsvName
        df = pd.read_csv ( dfg, header=None, index_col=None )
        df.columns = ['Filename', 'Station', 'pixelvalue']
        df.to_csv ( dfg, index=False )

        dfr = pd.read_csv ( dfg )
        kl = pd.crosstab ( dfr.Filename, dfr['Station'], values=dfr['pixelvalue'], aggfunc='mean' )
        kl.to_csv ( dfg, index=True )

    def graphplot_m_line(self):
        self.dlg.tsabuttonBox_m.clicked.connect(self.graphplot_m_line)
        self.dlg.lineEdit_tsa.setText ( self.inptsafolderName )
        self.dlg.lineEdit_tsa_out.setText ( self.newcsvName )
        jsve = self.newcsvName
        dfrm = pd.read_csv ( jsve )
        y = dfrm.columns[1:]
        for col in y:
            plt.plot( dfrm['Filename'], dfrm[col],marker='o' )
            plt.xlabel ( 'Raster file Name' )
            plt.ylabel ( 'Pixel Value' )
            plt.title ( 'Graphical Representation of variation in pixel value' )
            plt.legend ( y )
            plt.xticks (dfrm['Filename'], rotation=90 )
            plt.grid ( True )
            plt.show ()


    def graphplot_m_point(self):
        self.dlg.tsabuttonBox_m.clicked.connect(self.graphplot_m_point)
        self.dlg.lineEdit_tsa.setText ( self.inptsafolderName )
        self.dlg.lineEdit_tsa_out.setText ( self.newcsvName )
        jve = self.newcsvName
        dfm = pd.read_csv ( jve )
        y = dfm.columns[1:]
        for col in y:
            plt.scatter( dfm['Filename'], dfm[col], marker='o' )
            plt.xlabel ( 'Raster file Name' )
            plt.ylabel ( 'Pixel Value' )
            plt.title ( 'Graphical Representation of variation in pixel value' )
            plt.legend ( y )
            plt.xticks (dfm['Filename'], rotation=90 )
            plt.grid ( True )
            plt.show ()

    def graphplot_m_bar(self):
        self.dlg.tsabuttonBox_m.clicked.connect(self.graphplot_m_bar)
        self.dlg.lineEdit_tsa.setText ( self.inptsafolderName )
        self.dlg.lineEdit_tsa_out.setText ( self.newcsvName )
        je = self.newcsvName
        dfm = pd.read_csv ( je )
        y = dfm.columns[1:]
        dfm.set_index ( dfm['Filename'] )[y].plot.bar ()
        plt.show ()

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show ()
        # Run the dialog event loop
        result = self.dlg.exec_ ()
        # See if OK was pressed
        if result:
            pass

