import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import cv2

SRC = r"C:\Users\danie\Downloads\drive-download-20260602T184448Z-3-001"
PROJ = r"D:\VATSSA Website\palette"

TEAL  = np.array([1, 151, 176], float)    # #0197B0
GREEN = np.array([123, 215, 88], float)   # #7BD758
DARK  = (11, 42, 48)                       # #0B2A30
OFFW  = (248, 243, 240)                    # #F8F3F0
HEX_TEAL, HEX_GREEN, HEX_DARK, HEX_OFFW = "#0197B0", "#7BD758", "#0B2A30", "#F8F3F0"

# ---------- gradient helper (raster) ----------
def gradient(W, H):
    xs = np.linspace(0, 1, W)[None, :]
    ys = np.linspace(0, 1, H)[:, None]
    t = np.clip(0.5*xs + 0.5*(1-ys), 0, 1)        # bottom-left 0 -> top-right 1
    g = TEAL[None,None,:]*(1-t[...,None]) + GREEN[None,None,:]*t[...,None]
    return g.astype(np.uint8)

def fit_alpha(alpha, box_h):
    ys, xs = np.where(alpha > 8)
    crop = alpha[ys.min():ys.max()+1, xs.min():xs.max()+1]
    ch, cw = crop.shape
    scale = box_h/ch
    nw, nh = max(1,int(round(cw*scale))), box_h
    return np.array(Image.fromarray(crop).resize((nw,nh), Image.LANCZOS)), nw, nh

# ---------- contour -> SVG path (handles holes via even-odd) ----------
def mask_to_path(mask, sx, sy, tx, ty, eps=0.6, minarea=6):
    cnts,_ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    segs=[]
    for c in cnts:
        if cv2.contourArea(c) < minarea: continue
        c = cv2.approxPolyDP(c, eps, True).reshape(-1,2)
        if len(c) < 3: continue
        pts = " L ".join(f"{x*sx+tx:.1f} {y*sy+ty:.1f}" for x,y in c)
        segs.append("M " + pts + " Z")
    return " ".join(segs)

# ============ load official horizontal, split wordmark vs old africa ============
A = np.array(Image.open(SRC + r"\vatssa_logo_horizontal_black_transparent.png").convert("RGBA"))[:,:,3]
H_, W_ = A.shape
mask = A > 25
lab, n = ndimage.label(mask)
ys, xs = np.where(mask)
main_af = lab[ys[np.argmin(ys)], xs[np.argmin(ys)]]
africa_set = {main_af}
for i in range(1, n+1):
    cy, cx = np.where(lab == i)
    if cx.size and cx.min() > 1800 and cy.max() < 620:
        africa_set.add(i)
word_alpha = A.copy()
for i in africa_set:
    word_alpha[lab == i] = 0
yy_, xx_ = np.mgrid[0:H_, 0:W_]
word_alpha[(yy_ < 339) | ((xx_ > 1616) & (yy_ < 640))] = 0   # kill old-africa ghosts

# new africa silhouette
na = np.array(Image.open(PROJ + r"\_africa_new_silhouette.png").convert("RGBA"))[:,:,3]
nys, nxs = np.where(na > 8)
NA_X0, NA_Y0 = nxs.min(), nys.min()
NA_W, NA_H = nxs.max()-nxs.min()+1, nys.max()-nys.min()+1

GRAD_DEF = (f'<linearGradient id="vg" x1="0" y1="1" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{HEX_TEAL}"/>'
            f'<stop offset="1" stop-color="{HEX_GREEN}"/></linearGradient>')

# ============ 1) HORIZONTAL: raster + svg ============
bx0,bx1,by0,by1 = 1429,1986,74,620
box_h = by1-by0
af_scaled, nw, nh = fit_alpha(na, box_h)
ax0 = (bx0+bx1)//2 - nw//2
ay0 = by0
af_sx = box_h/NA_H            # scale applied to silhouette
def build_horizontal_png(word_rgb, fname):
    grad = gradient(nw, nh)
    af = np.zeros((H_,W_,4), np.uint8)
    af[ay0:ay0+nh, ax0:ax0+nw, :3] = grad
    af[ay0:ay0+nh, ax0:ax0+nw, 3]  = af_scaled
    wm = np.zeros((H_,W_,4), np.uint8)
    wm[...,0],wm[...,1],wm[...,2] = word_rgb
    wm[...,3] = word_alpha
    base = Image.fromarray(np.zeros((H_,W_,4),np.uint8),"RGBA")
    base.alpha_composite(Image.fromarray(wm,"RGBA"))
    base.alpha_composite(Image.fromarray(af,"RGBA"))
    base.save(PROJ+"\\"+fname); print("saved",fname)

def build_horizontal_svg(word_hex, fname):
    word_path = mask_to_path(word_alpha>120, 1,1,0,0, eps=0.6)
    # africa: silhouette space -> target box (subtract content origin, scale by af_sx, offset)
    af_tx = ax0 - NA_X0*af_sx
    af_ty = ay0 - NA_Y0*af_sx
    af_path = mask_to_path(na>120, af_sx, af_sx, af_tx, af_ty, eps=0.5)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_} {H_}" '
           f'width="{W_}" height="{H_}">\n<defs>{GRAD_DEF}</defs>\n'
           f'<path fill="{word_hex}" fill-rule="evenodd" d="{word_path}"/>\n'
           f'<path fill="url(#vg)" fill-rule="evenodd" d="{af_path}"/>\n</svg>\n')
    open(PROJ+"\\"+fname,"w",encoding="utf-8").write(svg); print("saved",fname,f"({len(svg)//1024} KB)")

build_horizontal_png(OFFW, "logo_horizontal_white.png")
build_horizontal_png(DARK, "logo_horizontal_dark.png")
build_horizontal_svg(HEX_OFFW, "logo_horizontal_white.svg")
build_horizontal_svg(HEX_DARK, "logo_horizontal_dark.svg")

# ============ 2) ICON: disc + gradient ring border + gradient Africa ============
RING_IN = 0.42          # inner radius (disc edge) as fraction of canvas
RING_W  = 0.045         # ring (gradient border) thickness as fraction of canvas
AF_BOXH = 0.58          # africa height as fraction of canvas
HEX_BG  = "#07262C"; BG_RGB = (7,38,44)

def build_icon_png(size, fname, disc=OFFW):           # disc=RGB tuple, or None for transparent
    SS=4; S=size*SS; c=S//2
    Rin=S*RING_IN; w=S*RING_W; Rout=Rin+w
    yy,xx=np.mgrid[0:S,0:S].astype(float)
    dist=np.sqrt((xx-c)**2+(yy-c)**2)
    img=Image.new("RGBA",(S,S),(0,0,0,0))
    if disc is not None:
        d=np.zeros((S,S,4),np.uint8); d[...,:3]=disc
        d[...,3]=np.where(dist<=Rin,255,0).astype(np.uint8)
        img.alpha_composite(Image.fromarray(d,"RGBA"))
    ring=np.zeros((S,S,4),np.uint8); ring[...,:3]=gradient(S,S)   # gradient border
    ring[...,3]=np.where((dist>=Rin)&(dist<=Rout),255,0).astype(np.uint8)
    img.alpha_composite(Image.fromarray(ring,"RGBA"))
    box_h=int(S*AF_BOXH)
    af,nw2,nh2=fit_alpha(na,box_h)
    afl=np.zeros((S,S,4),np.uint8)
    px=c-nw2//2; py=c-nh2//2
    afl[py:py+nh2,px:px+nw2,:3]=gradient(nw2,nh2)
    afl[py:py+nh2,px:px+nw2,3]=af
    img.alpha_composite(Image.fromarray(afl,"RGBA"))
    img=img.resize((size,size),Image.LANCZOS)
    img.save(PROJ+"\\"+fname); print("saved",fname)

def build_icon_svg(fname, disc_hex=HEX_OFFW, size=1024):   # disc_hex=None -> transparent
    c=size/2; Rin=size*RING_IN; w=size*RING_W; Rmid=Rin+w/2
    box_h=size*AF_BOXH; sx=box_h/NA_H
    nw2=NA_W*sx; nh2=NA_H*sx
    tx=(c-nw2/2)-NA_X0*sx; ty=(c-nh2/2)-NA_Y0*sx
    af_path=mask_to_path(na>120, sx, sx, tx, ty, eps=0.5)
    disc=(f'<circle cx="{c:.0f}" cy="{c:.0f}" r="{Rin:.1f}" fill="{disc_hex}"/>\n'
          if disc_hex else "")
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
         f'width="{size}" height="{size}">\n<defs>{GRAD_DEF}</defs>\n{disc}'
         f'<circle cx="{c:.0f}" cy="{c:.0f}" r="{Rmid:.1f}" fill="none" '
         f'stroke="url(#vg)" stroke-width="{w:.1f}"/>\n'
         f'<path fill="url(#vg)" fill-rule="evenodd" d="{af_path}"/>\n</svg>\n')
    open(PROJ+"\\"+fname,"w",encoding="utf-8").write(svg); print("saved",fname)

# ---- full-gradient-fill variant (gradient fills the whole tile; white disc + Africa knockout) ----
FILL_DISC = 0.42        # white disc radius as fraction of canvas (matches RING_IN)
FILL_AFH  = 0.58        # africa height as fraction of canvas (matches AF_BOXH)
def build_icon_fill(size, fname):
    SS=4; S=size*SS; c=S//2
    img=Image.fromarray(np.dstack([gradient(S,S), np.full((S,S),255,np.uint8)]),"RGBA")
    yy,xx=np.mgrid[0:S,0:S].astype(float)
    dist=np.sqrt((xx-c)**2+(yy-c)**2)
    disc=dist<=S*FILL_DISC
    af,nw,nh=fit_alpha(na,int(S*FILL_AFH))
    afm=np.zeros((S,S),bool); px=c-nw//2; py=c-nh//2; afm[py:py+nh,px:px+nw]=af>120
    white=disc&~afm
    wl=np.zeros((S,S,4),np.uint8); wl[...,:3]=OFFW; wl[...,3]=np.where(white,255,0).astype(np.uint8)
    img.alpha_composite(Image.fromarray(wl,"RGBA"))
    img.resize((size,size),Image.LANCZOS).save(PROJ+"\\"+fname); print("saved",fname)

def build_icon_fill_svg(fname, size=1024):
    c=size/2; r=size*FILL_DISC
    sx=(size*FILL_AFH)/NA_H; nw=NA_W*sx; nh=NA_H*sx
    tx=(c-nw/2)-NA_X0*sx; ty=(c-nh/2)-NA_Y0*sx
    af_path=mask_to_path(na>120, sx, sx, tx, ty, eps=0.5)
    circ=f"M {c-r:.1f} {c:.1f} a {r:.1f} {r:.1f} 0 1 0 {2*r:.1f} 0 a {r:.1f} {r:.1f} 0 1 0 {-2*r:.1f} 0 Z"
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">\n'
         f'<defs>{GRAD_DEF}</defs>\n<rect width="{size}" height="{size}" fill="url(#vg)"/>\n'
         f'<path fill="{HEX_OFFW}" fill-rule="evenodd" d="{circ} {af_path}"/>\n</svg>\n')
    open(PROJ+"\\"+fname,"w",encoding="utf-8").write(svg); print("saved",fname)

# white-disc variant (disc + gradient ring; sits on theme background)
build_icon_png(1024,"logo_icon.png", OFFW)
build_icon_png(512,"logo_icon_512.png", OFFW)
build_icon_png(180,"logo_icon_180.png", OFFW)
build_icon_svg("logo_icon.svg", HEX_OFFW)
# full-gradient-fill variant
build_icon_fill(1024,"logo_icon_fill.png")
build_icon_fill(180,"logo_icon_fill_180.png")
build_icon_fill_svg("logo_icon_fill.svg")

# ============ preview ============
def preview(bg, horiz, out):
    base=Image.new("RGBA",(1400,420),bg)
    im=Image.open(PROJ+"\\"+horiz).convert("RGBA")
    sc=min(950/im.width,240/im.height); im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
    base.alpha_composite(im,(60,90))
    ic=Image.open(PROJ+r"\logo_icon.png").convert("RGBA").resize((240,240),Image.LANCZOS)
    base.alpha_composite(ic,(1110,90))
    base.convert("RGB").save(PROJ+"\\"+out); print("saved",out)
preview((11,42,48,255),"logo_horizontal_white.png","_preview_dark.png")
preview((248,243,240,255),"logo_horizontal_dark.png","_preview_light.png")
print("DONE")
