"""Categorias padrão do sistema (T-008, `spec.md` §6.3).

Criadas como cópias do usuário na inscrição e totalmente editáveis.
"""

from sqlalchemy.orm import Session

from app.models import Category, User

INCOME = ["Salário", "Freelance/Extras", "Rendimentos", "Outras receitas"]

FIXED_EXPENSES = [
    "Moradia (aluguel/condomínio)",
    "Água e energia",
    "Celular/internet",
    "Plano de saúde",
    "Plano odontológico",
    "Academia",
    "Veículo/parcela",
    "Assinaturas",
    "Outras despesas fixas",
]

VARIABLE_EXPENSES = [
    "Alimentação",
    "Lanches/restaurantes",
    "Transporte/combustível",
    "Saúde",
    "Educação",
    "Beleza/cuidados pessoais",
    "Serviços domésticos",
    "Lazer",
    "Compras diversas",
    "Extras",
]

INVESTMENTS = [
    "Poupança",
    "Reserva de emergência",
    "Objetivos e reservas",
    "Outros investimentos",
]


def seed_default_categories(db: Session, user: User) -> None:
    for name in INCOME:
        db.add(
            Category(
                user_id=user.id,
                name=name,
                group_type="income",
                is_default=True,
            )
        )
    for name in FIXED_EXPENSES:
        db.add(
            Category(
                user_id=user.id,
                name=name,
                group_type="expense",
                expense_type="fixed",
                is_default=True,
            )
        )
    for name in VARIABLE_EXPENSES:
        db.add(
            Category(
                user_id=user.id,
                name=name,
                group_type="expense",
                expense_type="variable",
                is_default=True,
            )
        )
    for name in INVESTMENTS:
        db.add(
            Category(
                user_id=user.id,
                name=name,
                group_type="investment",
                is_default=True,
            )
        )
    db.commit()
