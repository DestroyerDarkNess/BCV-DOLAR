import os
import flet as ft
import asyncio
from core.bcv import BCV
# import locale  # Asegúrate de importar la biblioteca locale
from asyncio.exceptions import TimeoutError

# Configura el locale a español
# locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Cambia según tu sistema operativo

async def fetch_exchange_data():
    bcv = BCV()
    data = await bcv.get_data()
    return data

def main(page: ft.Page):
    page.title = "Tipo de Cambio - BCV"
    page.window_left = 942
    page.window_top = 96
    page.window.width = 390
    page.window.resizable = False
    page.window.maximizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Placeholder para actualizar con datos reales
    exchange_rates_container = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # Placeholder para el texto de la fecha
    date_text = ft.Text(
        "Fecha Valor: Cargando...",
        size=14,
        weight=ft.FontWeight.W_600,
        text_align=ft.TextAlign.CENTER,
    )

    # Placeholder para el indicador de progreso
    progress_indicator = ft.ProgressRing(visible=False)

    # Estado para evitar recargas concurrentes
    is_loading = [False]  # Usamos una lista para modificar el estado global

    def get_symbol_by_id(money_id):
        match money_id:
            case "EUR":
                return "€"
            case "CNY":
                return "¥"
            case "TRY":
                return "₺"
            case "RUB":
                return "₽"
            case "USD":
                return "$"
        return ""

    # Función para cargar datos en la interfaz
    async def load_data():
        if is_loading[0]:
            return  # Evitar múltiples recargas simultáneas

        is_loading[0] = True  # Marcar como cargando
        progress_indicator.visible = True  # Mostrar el indicador de progreso
        exchange_rates_container.controls.clear()  # Limpiar datos anteriores
        date_text.value = "Fecha Valor: Cargando..."
        page.update()  # Refrescar la interfaz con el indicador visible

        try:
            # Intentar cargar los datos con un timeout de 5 segundos
            data = await asyncio.wait_for(fetch_exchange_data(), timeout=5)

            if data:
                # Extraer la fecha (es la misma para todas las monedas)
                first_currency = next(iter(data.values()))  # Obtén el primer elemento
                if first_currency.Date is not None:
                    date_text.value = f"Fecha Valor: {first_currency.Date.strftime('%A, %d %B %Y')}"

                for money_id, money_data in data.items():
                    money_id = money_data.ID.replace(" ", "")
                    money_symbol = get_symbol_by_id(money_id)

                    exchange_rates_container.controls.append(
                        ft.Row(
                            [
                                ft.Text(f"{money_symbol} {money_id}", size=16),
                                ft.Text(money_data.Value, size=16, weight=ft.FontWeight.BOLD),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        )
                    )
            else:
                exchange_rates_container.controls.append(
                    ft.Text("No se pudieron obtener los datos.", size=16, color=ft.colors.RED)
                )
        except TimeoutError:
            # Mensaje de error si ocurre un timeout
            exchange_rates_container.controls.append(
                ft.Text("Error: Tiempo de conexión agotado.", size=16, color=ft.colors.RED)
            )
        except Exception as e:
            # Mensaje de error para cualquier otra excepción
            exchange_rates_container.controls.append(
                ft.Text(f"Error: {str(e)}", size=16, color=ft.colors.RED)
            )
        finally:
            # Ocultar el indicador de progreso
            progress_indicator.visible = False
            is_loading[0] = False
            page.update()  # Refrescar la interfaz con el indicador oculto y los datos actualizados

    # Envolviendo la tarea de datos para evitar advertencias
    def load_data_wrapper(e):
        asyncio.run(load_data())

    # FloatingActionButton para refrescar datos
    refresh_button = ft.FloatingActionButton(
        icon=ft.icons.REFRESH,
        on_click=load_data_wrapper,
        bgcolor=ft.colors.BLUE,  # Color de fondo del botón
        tooltip="Actualizar datos",  # Texto al pasar el mouse
        mini=True,
    )

    # Main Card
    card = ft.Container(
        width=500,
        padding=ft.padding.only(top=50),
        border_radius=10,
        content=ft.Column(
            [
                # Logo and Title
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "Tipo de Cambio de Referencia",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Image(
                                src="https://i.ibb.co/n1QTVH5/logo-bcv-04-2-modified.png",
                                width=100,
                                height=100,
                            ),
                            ft.Text(
                                "BANCO CENTRAL DE VENEZUELA",
                                size=16,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "El tipo de cambio publicado por el BCV es el promedio ponderado resultante de las operaciones diarias de las mesas de cambio activas de las instituciones bancarias participantes.",
                                size=14,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ]
                    ),
                ),
                ft.Divider(),
                # Indicador de progreso
                progress_indicator,
                # Contenedor de datos dinámicos
                exchange_rates_container,
                ft.Divider(),
                date_text,  # Texto de la fecha
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # Añadir contenido y botón flotante
    page.add(card)
    page.floating_action_button = refresh_button
    page.update()
    load_data_wrapper(None)
    
ft.app(target=main)