def get_stylesheet(theme="dark"):
    if theme == "dark":
        return """
        QDialog, QWidget {
            background-color: #202020;
            color: #FFFFFF;
            font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
            font-size: 13px;
        }

        /* QTabWidget */
        QTabWidget::pane {
            border: 1px solid #333333;
            background-color: #262626;
            border-radius: 8px;
            top: -1px;
        }

        QTabBar::tab {
            background-color: transparent;
            color: #A0A0A0;
            padding: 8px 16px;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            margin-right: 4px;
        }

        QTabBar::tab:hover {
            color: #FFFFFF;
            background-color: #2A2A2A;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }

        QTabBar::tab:selected {
            color: #60CDFF;
            font-weight: 600;
            border-bottom: 2px solid #60CDFF;
        }

        /* Group Box / Cards */
        QGroupBox {
            background-color: #2B2B2B;
            border: 1px solid #383838;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 16px;
            font-weight: 600;
            color: #FFFFFF;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 0 4px;
            color: #60CDFF;
        }

        /* CheckBox */
        QCheckBox {
            spacing: 10px;
            color: #E0E0E0;
            background: transparent;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #555555;
            border-radius: 4px;
            background-color: #2D2D2D;
        }
        QCheckBox::indicator:hover {
            border-color: #60CDFF;
        }
        QCheckBox::indicator:checked {
            background-color: #0078D4;
            border-color: #0078D4;
            image: none;
        }

        /* ComboBox */
        QComboBox {
            background-color: #2D2D2D;
            border: 1px solid #444444;
            border-radius: 6px;
            padding: 6px 12px;
            color: #FFFFFF;
            min-height: 20px;
        }
        QComboBox:hover {
            border-color: #60CDFF;
            background-color: #323232;
        }
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        QComboBox QAbstractItemView {
            background-color: #2D2D2D;
            border: 1px solid #444444;
            border-radius: 6px;
            selection-background-color: #0078D4;
            selection-color: #FFFFFF;
            color: #FFFFFF;
            padding: 4px;
            outline: none;
        }

        /* Buttons */
        QPushButton {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #444444;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 500;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #383838;
            border-color: #555555;
        }
        QPushButton:pressed {
            background-color: #242424;
        }
        QPushButton#primaryBtn {
            background-color: #0078D4;
            color: #FFFFFF;
            border: 1px solid #006CBD;
            font-weight: 600;
        }
        QPushButton#primaryBtn:hover {
            background-color: #1A86D9;
        }
        QPushButton#primaryBtn:pressed {
            background-color: #0060AA;
        }

        /* Labels */
        QLabel {
            color: #CCCCCC;
            background: transparent;
        }
        QLabel#headerLabel {
            font-size: 16px;
            font-weight: bold;
            color: #FFFFFF;
        }
        QLabel#subHeaderLabel {
            font-size: 11px;
            color: #888888;
        }

        /* ScrollBar */
        QScrollBar:vertical {
            border: none;
            background: #202020;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #444444;
            min-height: 20px;
            border-radius: 4px;
        }
        """
    else: # Light theme
        return """
        QDialog, QWidget {
            background-color: #F3F3F3;
            color: #1A1A1A;
            font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
            font-size: 13px;
        }

        QTabWidget::pane {
            border: 1px solid #E0E0E0;
            background-color: #FFFFFF;
            border-radius: 8px;
            top: -1px;
        }

        QTabBar::tab {
            background-color: transparent;
            color: #5A5A5A;
            padding: 8px 16px;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            margin-right: 4px;
        }

        QTabBar::tab:hover {
            color: #000000;
            background-color: #EAEAEA;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }

        QTabBar::tab:selected {
            color: #0067C0;
            font-weight: 600;
            border-bottom: 2px solid #0067C0;
        }

        QGroupBox {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 16px;
            font-weight: 600;
            color: #1A1A1A;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 0 4px;
            color: #0067C0;
        }

        QCheckBox {
            spacing: 10px;
            color: #222222;
            background: transparent;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #BBBBBB;
            border-radius: 4px;
            background-color: #FFFFFF;
        }
        QCheckBox::indicator:hover {
            border-color: #0067C0;
        }
        QCheckBox::indicator:checked {
            background-color: #0067C0;
            border-color: #0067C0;
        }

        QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 6px 12px;
            color: #1A1A1A;
            min-height: 20px;
        }
        QComboBox:hover {
            border-color: #0067C0;
        }
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            selection-background-color: #0067C0;
            selection-color: #FFFFFF;
            color: #1A1A1A;
            padding: 4px;
        }

        QPushButton {
            background-color: #FFFFFF;
            color: #1A1A1A;
            border: 1px solid #D0D0D0;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 500;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #F8F8F8;
            border-color: #BBBBBB;
        }
        QPushButton:pressed {
            background-color: #EEEEEE;
        }
        QPushButton#primaryBtn {
            background-color: #0067C0;
            color: #FFFFFF;
            border: 1px solid #005A9E;
            font-weight: 600;
        }
        QPushButton#primaryBtn:hover {
            background-color: #1879D6;
        }
        QPushButton#primaryBtn:pressed {
            background-color: #004F8B;
        }

        QLabel {
            color: #444444;
            background: transparent;
        }
        QLabel#headerLabel {
            font-size: 16px;
            font-weight: bold;
            color: #111111;
        }
        QLabel#subHeaderLabel {
            font-size: 11px;
            color: #666666;
        }
        """
