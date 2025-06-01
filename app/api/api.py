import os
from typing import Annotated

from fastapi import APIRouter, Path, Query, Request, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.schemas.resumeio import Extension
from app.services.resumeio import ResumeioDownloader

router = APIRouter()
templates = Jinja2Templates(directory="templates")

SAVE_DIR = "saved_resumes"  # Direktori untuk menyimpan file PDF
os.makedirs(SAVE_DIR, exist_ok=True)  # Pastikan direktori ada

# Endpoint untuk mengunduh resume yang sudah disimpan
@router.get("/download-local/{filename}")
def download_local_resume(filename: Annotated[str, Path()]):
    """
    Mengunduh file PDF resume yang sudah disimpan.

    Parameters
    ----------
    filename : str
        Nama file yang akan diunduh.

    Returns
    -------
    FileResponse
        File PDF yang diminta.
    """
    file_path = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(file_path):
        return Response(content="File not found", status_code=404)
    
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

# show list of saved resumes using json response
@router.get("/list")
def list_resumes(request: Request):
    """
    List all saved resumes.

    Returns
    -------
    List[str]
        List of all saved resumes.
    """
    # return os.listdir(SAVE_DIR)
    return templates.TemplateResponse("list.html", {"request": request, "resumes": os.listdir(SAVE_DIR)})

@router.post("/download/{rendering_token}")
def download_resume(
    rendering_token: Annotated[str, Path(min_length=24, max_length=24, pattern="^[a-zA-Z0-9]{24}$")],
    image_size: Annotated[int, Query(gt=0)] = 3000,
    extension: Annotated[Extension, Query(...)] = Extension.jpeg,
):
    """
    Download a resume from resume.io, save it, and return it as a PDF.

    Parameters
    ----------
    rendering_token : str
        Rendering Token of the resume to download.
    image_size : int, optional
        Size of the images to download, by default 3000.
    extension : str, optional
        Image extension to download, by default "jpg".

    Returns
    -------
    fastapi.responses.Response
        A PDF representation of the resume with appropriate headers for inline display.
    """
    resumeio = ResumeioDownloader(rendering_token=rendering_token, image_size=image_size, extension=extension)
    pdf_data = resumeio.generate_pdf()

    # Simpan file ke sistem
    file_path = os.path.join(SAVE_DIR, f"{rendering_token}.pdf")
    with open(file_path, "wb") as f:
        f.write(pdf_data)

    return Response(
        pdf_data,
        headers={"Content-Disposition": f'inline; filename="{rendering_token}.pdf"'},
    )

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    """
    Render the main index page.

    Parameters
    ----------
    request : fastapi.Request
        The request instance.

    Returns
    -------
    fastapi.templating.Jinja2Templates.TemplateResponse
        Rendered template of the main index page.
    """
    return templates.TemplateResponse("index.html", {"request": request})
