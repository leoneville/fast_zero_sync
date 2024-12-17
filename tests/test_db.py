from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(
        username='neville',
        email='leo@ville.com',
        password='minha_senha-123',
    )
    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.email == 'leo@ville.com'))

    assert result.username == 'neville'
