import graphics as gr
window = gr.GraphWin("Fractal Rectangle", 300, 300)

def fractal_rectangle(A, B, C, D,  depth=10):
    if depth < 1:
        return
    # gr.Line(gr.Point(*A), gr.Point(*B)).draw(window)
    # gr.Line(gr.Point(*B), gr.Point(*C)).draw(window)
    # gr.Line(gr.Point(*C), gr.Point(*D)).draw(window)
    # gr.Line(gr.Point(*D), gr.Point(*A)).draw(window)
    for M,N in (A, B), (B,C), (C,D), (D,A):
        gr.Line(gr.Point(*M), gr.Point(*N)).draw(window)
