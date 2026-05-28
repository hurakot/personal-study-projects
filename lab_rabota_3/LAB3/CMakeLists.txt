cmake_minimum_required(VERSION 3.16)

project(LabRabota3 VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Network)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Network)

set(PROJECT_SOURCES
    main.cpp
    mainwindow.cpp
    mainwindow.h
    mainwindow.ui
    httpclient.cpp
    httpclient.h
    nerf.cpp
    nerf.h
    nerfdialog.cpp
    nerfdialog.h
    nerfdialog.ui
)

if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
    qt_add_executable(LabRabota3
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
        nerfdialog.h nerfdialog.cpp

    )
else()
    add_executable(LabRabota3
        ${PROJECT_SOURCES}
    )
endif()

target_link_libraries(LabRabota3 PRIVATE
    Qt${QT_VERSION_MAJOR}::Widgets
    Qt${QT_VERSION_MAJOR}::Network
)

set_target_properties(LabRabota3 PROPERTIES
    WIN32_EXECUTABLE TRUE
    MACOSX_BUNDLE TRUE
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_finalize_executable(LabRabota3)
endif()
