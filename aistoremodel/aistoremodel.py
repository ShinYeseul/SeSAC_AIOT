from sqlalchemy import Column, Integer, String, ForeignKey

import flask
from sqlalchemy_utils import PasswordType, force_auto_coercion
from database import Base, db_session
from sqlalchemy.orm import relationship

class AiStore(Base):
    __tablename__ = 'stores'
    s_id = Column(String(20),primary_key=True) # 문자열(20), 주키 설정 하여 컬럼 생성
    name = Column(String(20))
    locate = Column(String(30))
    sPassword = Column(PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],

        deprecated=['md5_crypt']
    ))
    products_num = Column(Integer) #숫자형 컬럼 생성

    def __init__(self, s_id, name, locate,sPassword):
        self.s_id = s_id
        self.name = name
        self.locate = locate
        self.sPassword = sPassword
        self.products_num = 0

    def add_product(self):
        self.products_num += 1

class Products(Base):
    __tablename__ = 'products'
    p_id = Column(String(20), primary_key=True)
    name = Column(String(20))
    reco_price = Column(Integer)

class Inventory(Base):
    __tablename__ = 'inventory'
    p_id = Column(String(20), ForeignKey(Products.p_id), primary_key=True,)
    count = Column(Integer)
    price = Column(Integer)
    s_id = Column(String(20),ForeignKey(AiStore.s_id),primary_key=True)# 문자열(20), 외래키(AiStore.s_id), 주키 설정 하여 컬럼 생성
    product = relationship('Products') # products 테이블과 관계 형성되어 자동 조인(products 테이블의 주키가 외래키로 설정되어있어야함)

    def __init__(self, p_id, count, price, s_id):
        self.p_id = p_id
        self.count = count
        self.price = price
        self.s_id = s_id

    def __repr__(self):
        return '<{}, {}, {}, {}>'.format(self.p_id, self.count, self.price,self.s_id)

    def add_count(self, count):
        self.count += count

    def sub_count(self, count):
        self.count -= count

def create_store(s_id, s_name, locate,Password):
    # s_id 가 존재 하지 않는 경우만 AiStore 인스턴스 생성후 데이터베이스에 추가
    # 커밋하여 데이터베이스 적용

    if db_session.get(AiStore, s_id) is None:
        store = AiStore(s_id,s_name,locate,Password)
        db_session.add(store)
        db_session.commit()

def show_list(s_id = None):
    if s_id is None:
        stores = AiStore.query.all()
        return str(stores)
    else:
        store = db_session.get(AiStore, s_id)
        return [store]

def get_menu(s_id):
    # app의 board와 manage 페이지에서 스토어가 가진 상품을 보여주기 위한 menu 리스트 생성 함수

    # Inventory의 s_id가 파라미터의 s_id와 같은 Inventory 쿼리
    # .query.filter 함수 활용할 것
    # Inventory의 product 컬럼은 Products와 관계가 형성 되있으므로 자동조인됨
    # 관계 사용 안할시 다음과 같은 조인방식으로 가능
    # invs = db_session.query(Inventory.p_id, Inventory.price, Inventory.count, Products.product).join(Products, Inventory.p_id == Products.p_id)

    invs = Inventory.query.filter(Inventory.s_id == s_id)

    # menu 는 쿼리된 inventory의 각각의 상품을 딕셔너리로 보관하는 리스트
    # 'p_id','p_name','price','count' 의 키를 가지는 딕셔너리
    # 'p_name' 의 값은 inventory 하나의 인스턴스에서 .product.name 컬럼값으로 할당(inventory orm의 자동조인된 porduct컬럼의 name 컬럼)
    menu = []
    for i in invs:
        m={}
        m['p_id'] = i.p_id
        m['p_name'] = i.product.name
        m['price'] = i.price
        m['count'] = i.count
        menu.append(m)
        print(menu)

    return menu


def set_product(s_id, p_id, price, count):
    # 상품이 있는경우 가격및 재고 변경
    # 상품이 없는경우 상품 생성후 추가

    # 파라미터로 입력된 s_id, p_id 값을 가지는 Inventory 쿼리 또는 get
    inventory = db_session.get(Inventory, (p_id, s_id))

    # 쿼리된 Inventory가 있으면 입력된 가격으로 가격 변경및 입력된 재고만큼 재고 추가
    # 없으면 입력된 가격 및 재고로 새로운 Inventory orm 생성후 데이터베이스에 add
    # 없을때 상품 생성후 스토어의 product_num도 +1 (함수 사용)

    if inventory is not None:
        inventory.add_count(count)
        inventory.price = price
    else:
        i = Inventory(p_id = p_id, count = count, price=price,s_id=s_id)
        db_session.add(i)

    # 최종 커밋하여 데이터베이스 적용
    db_session.commit()

def buy_product(p_id, s_id, count):
    # 입력된 재고 이상이 있을때 상품 구매
    # 파라미터로 입력된 s_id, p_id 값을 가지는 Inventory 쿼리 또는 get
    # inventory orm 의 재고가 입력된 재고 보다 클때 입력된 재고만큼 차감(함수 사용)
    # 커밋하여 데이터베이스 적용
    inventory = db_session.get(Inventory, (p_id, s_id))

    if inventory.count > count:
        inventory.sub_count(count)
        db_session.commit()
        return True
    else:
        return False

# if __name__ == '__main__':
#     show_list()