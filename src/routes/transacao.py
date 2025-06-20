from flask import Blueprint, request, jsonify
from src.models.transacao import db, Transacao
from datetime import datetime

transacao_bp = Blueprint('transacao', __name__)

@transacao_bp.route('/transacoes', methods=['GET'])
def listar_transacoes():
    """Lista todas as transações"""
    try:
        transacoes = Transacao.query.order_by(Transacao.data.desc()).all()
        return jsonify([transacao.to_dict() for transacao in transacoes])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@transacao_bp.route('/transacoes', methods=['POST'])
def adicionar_transacao():
    """Adiciona uma nova transação"""
    try:
        dados = request.get_json()
        
        # Validação dos dados
        if not dados or not all(k in dados for k in ('descricao', 'valor', 'tipo', 'categoria')):
            return jsonify({'erro': 'Dados incompletos'}), 400
        
        if dados['tipo'] not in ['receita', 'despesa']:
            return jsonify({'erro': 'Tipo deve ser receita ou despesa'}), 400
        
        if dados['valor'] <= 0:
            return jsonify({'erro': 'Valor deve ser positivo'}), 400
        
        # Criar nova transação
        nova_transacao = Transacao(
            descricao=dados['descricao'],
            valor=float(dados['valor']),
            tipo=dados['tipo'],
            categoria=dados['categoria'],
            data=datetime.utcnow()
        )
        
        db.session.add(nova_transacao)
        db.session.commit()
        
        return jsonify(nova_transacao.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@transacao_bp.route('/saldo', methods=['GET'])
def obter_saldo():
    """Calcula e retorna o saldo atual"""
    try:
        receitas = db.session.query(db.func.sum(Transacao.valor)).filter_by(tipo='receita').scalar() or 0
        despesas = db.session.query(db.func.sum(Transacao.valor)).filter_by(tipo='despesa').scalar() or 0
        saldo = receitas - despesas
        
        return jsonify({
            'saldo': saldo,
            'receitas': receitas,
            'despesas': despesas
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@transacao_bp.route('/transacoes/<int:transacao_id>', methods=['DELETE'])
def deletar_transacao(transacao_id):
    """Deleta uma transação específica"""
    try:
        transacao = Transacao.query.get_or_404(transacao_id)
        db.session.delete(transacao)
        db.session.commit()
        
        return jsonify({'mensagem': 'Transação deletada com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@transacao_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """Lista todas as categorias únicas"""
    try:
        categorias = db.session.query(Transacao.categoria).distinct().all()
        categorias_lista = [categoria[0] for categoria in categorias]
        return jsonify(categorias_lista)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

