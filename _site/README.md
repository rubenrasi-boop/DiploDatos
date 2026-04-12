# 📚 Mirror local de material externo

Esta carpeta contiene una copia local de recursos provenientes de
fuentes externas, guardada acá para consulta offline y búsqueda rápida
por texto. No forma parte de ningún entregable ni de los scripts del
repositorio.

## Estructura

```
_site/
├── README.md                          ← este archivo
├── Curso_ ... .htm                    ← snapshots HTML de páginas
├── Tema_ ... .htm                     ← del aula virtual (Moodle)
│
└── filminas/                          ← ver filminas/README.md
    ├── README.md
    └── clase{1..4}_{tema}.{pdf,txt}
```

## Cómo actualizar el mirror

### Snapshots HTML del aula virtual

Los archivos `.htm` y sus carpetas `*_files/` son `Save As → Webpage,
Complete` del navegador sobre cada página del aula virtual. Para
actualizarlos, abrir la página correspondiente y volver a guardar
encima del archivo existente.

### Filminas

Los PDFs y TXT se regeneran directamente desde Google Slides vía el
endpoint `/export/{pdf,txt}`. Ver las instrucciones en
[`filminas/README.md`](filminas/README.md).
